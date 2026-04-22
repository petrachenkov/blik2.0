import asyncio
import aiohttp
from aiohttp import web
from backend.config.settings import settings
from backend.database import get_db, async_session_maker
from backend.services import UserService, TicketService, ad_auth_service, max_bot_service
from backend.models.ticket import TicketStatus
import json


class MAXBot:
    """MAX Messenger Bot for IT Support"""
    
    def __init__(self):
        self.webhook_path = "/webhook/max"
        self.base_url = settings.MAX_WEBHOOK_URL or "http://localhost:8000"
        self.app = None
    
    async def handle_webhook(self, request: web.Request) -> web.Response:
        """Handle incoming webhook from MAX messenger"""
        try:
            data = await request.json()
            
            # Extract message data (adjust based on actual MAX API format)
            chat_id = data.get('chat', {}).get('id') or data.get('from', {}).get('id')
            message_text = data.get('text', '')
            message_id = data.get('message_id') or data.get('id')
            callback_data = data.get('callback_query', {}).get('data')
            
            if not chat_id:
                return web.json_response({"status": "error", "message": "No chat_id"})
            
            # Handle callback queries
            if callback_data:
                return await self.handle_callback(chat_id, callback_data, message_id)
            
            # Handle regular messages
            if message_text:
                response = await self.handle_message(chat_id, message_text, message_id)
                return web.json_response(response)
            
            return web.json_response({"status": "ok"})
            
        except Exception as e:
            print(f"Webhook error: {e}")
            return web.json_response({"status": "error", "message": str(e)})
    
    async def handle_message(self, chat_id: str, text: str, message_id: str) -> dict:
        """Handle incoming text message"""
        
        async with async_session_maker() as db:
            user_service = UserService(db)
            user = await user_service.get_by_telegram_id(chat_id)
            
            # Check if user is registered
            if not user:
                return await self.send_registration_message(chat_id)
            
            # Handle ticket creation flow
            if text.lower() in ['/start', 'меню', 'главное меню']:
                return await self.show_main_menu(chat_id, user.ad_full_name or user.ad_username)
            
            elif text.lower() == 'новая заявка':
                return await self.start_ticket_creation(chat_id)
            
            elif text.lower() == 'мои заявки':
                return await self.show_user_tickets(chat_id, user.id)
            
            elif text.lower() == 'помощь':
                return await self.show_help(chat_id)
            
            else:
                # If user is in ticket creation flow, handle description
                # For simplicity, treat any other message as potential ticket
                return await self.create_ticket_from_message(chat_id, user.id, text, message_id)
    
    async def handle_callback(self, chat_id: str, callback_data: str, message_id: str) -> web.Response:
        """Handle callback query from inline keyboard"""
        
        if callback_data == 'new_ticket':
            return await self.start_ticket_creation(chat_id)
        elif callback_data == 'my_tickets':
            async with async_session_maker() as db:
                user_service = UserService(db)
                user = await user_service.get_by_telegram_id(chat_id)
                if user:
                    return await self.show_user_tickets(chat_id, user.id)
        elif callback_data == 'help':
            return await self.show_help(chat_id)
        elif callback_data.startswith('ticket_status_'):
            ticket_id = int(callback_data.split('_')[-1])
            return await self.show_ticket_status(chat_id, ticket_id)
        
        return web.json_response({"status": "ok"})
    
    async def send_registration_message(self, chat_id: str) -> dict:
        """Send registration/authorization message"""
        text = """👋 Добро пожаловать в систему <b>Блик</b>!

Для начала работы необходимо авторизоваться через Active Directory.

Нажмите кнопку ниже для подключения."""
        
        buttons = [[("🔐 Авторизоваться", "auth")]]
        await max_bot_service.send_keyboard(chat_id, text, buttons)
        
        return {"status": "ok", "action": "registration_required"}
    
    async def show_main_menu(self, chat_id: str, username: str) -> dict:
        """Show main menu"""
        text = f"""👤 <b>{username}</b>, добро пожаловать в Блик!

Выберите действие:"""
        
        buttons = [
            ["📝 Новая заявка", "📋 Мои заявки"],
            ["❓ Помощь"]
        ]
        await max_bot_service.send_keyboard(chat_id, text, buttons)
        
        return {"status": "ok"}
    
    async def start_ticket_creation(self, chat_id: str) -> dict:
        """Start ticket creation flow"""
        text = """📝 <b>Создание новой заявки</b>

Пожалуйста, опишите вашу проблему:
- Что случилось?
- Какое оборудование/ПО затронуто?
- Срочность проблемы"""
        
        await max_bot_service.send_message(chat_id, text)
        
        return {"status": "ok", "action": "waiting_description"}
    
    async def create_ticket_from_message(
        self,
        chat_id: str,
        user_id: int,
        description: str,
        message_id: str
    ) -> dict:
        """Create ticket from user message"""
        async with async_session_maker() as db:
            ticket_service = TicketService(db)
            
            # Use first 50 chars of description as subject
            subject = description[:50] + "..." if len(description) > 50 else description
            
            ticket = await ticket_service.create_ticket(
                user_id=user_id,
                subject=subject,
                description=description,
                messenger_chat_id=chat_id,
                messenger_message_id=message_id
            )
            
            text = f"""✅ <b>Заявка #{ticket.id} создана!</b>

Тема: {ticket.subject}
Статус: {ticket.status.value}

Вы получите уведомление при изменении статуса."""
            
            await max_bot_service.send_message(chat_id, text)
            
            # Notify admins about new ticket (optional)
            # await self.notify_admins(ticket)
            
            return {"status": "ok", "ticket_id": ticket.id}
    
    async def show_user_tickets(self, chat_id: str, user_id: int) -> dict:
        """Show user's tickets"""
        async with async_session_maker() as db:
            ticket_service = TicketService(db)
            tickets = await ticket_service.get_user_tickets(user_id)
            
            if not tickets:
                await max_bot_service.send_message(
                    chat_id,
                    "📭 У вас пока нет заявок"
                )
                return {"status": "ok"}
            
            text = "📋 <b>Ваши заявки:</b>\n\n"
            buttons = []
            
            for ticket in tickets[:10]:  # Show last 10 tickets
                status_emoji = {
                    TicketStatus.NEW: "🆕",
                    TicketStatus.IN_PROGRESS: "⏳",
                    TicketStatus.WAITING_USER: "⏸️",
                    TicketStatus.RESOLVED: "✅",
                    TicketStatus.CLOSED: "🔒"
                }.get(ticket.status, "📄")
                
                text += f"{status_emoji} #{ticket.id} - {ticket.subject}\n"
                text += f"   Статус: {ticket.status.value}\n\n"
                
                buttons.append([f"📊 Статус #{ticket.id}"])
            
            await max_bot_service.send_keyboard(chat_id, text, buttons)
            
            return {"status": "ok"}
    
    async def show_ticket_status(self, chat_id: str, ticket_id: int) -> dict:
        """Show detailed ticket status"""
        async with async_session_maker() as db:
            ticket_service = TicketService(db)
            ticket = await ticket_service.get_ticket(ticket_id)
            
            if not ticket:
                await max_bot_service.send_message(chat_id, "Заявка не найдена")
                return {"status": "ok"}
            
            admin_name = ticket.assigned_admin.ad_full_name if ticket.assigned_admin else "Не назначен"
            
            text = f"""📊 <b>Заявка #{ticket.id}</b>

<b>Тема:</b> {ticket.subject}
<b>Описание:</b> {ticket.description}
<b>Статус:</b> {ticket.status.value}
<b>Приоритет:</b> {ticket.priority.value}
<b>Ответственный:</b> {admin_name}
<b>Создана:</b> {ticket.created_at.strftime('%d.%m.%Y %H:%M')}"""
            
            if ticket.resolved_at:
                text += f"\n<b>Решена:</b> {ticket.resolved_at.strftime('%d.%m.%Y %H:%M')}"
            
            await max_bot_service.send_message(chat_id, text)
            
            return {"status": "ok"}
    
    async def show_help(self, chat_id: str) -> dict:
        """Show help message"""
        text = """❓ <b>Помощь</b>

Система <b>Блик</b> - ваш помощник для создания заявок на IT обслуживание.

<b>Возможности:</b>
• Создание новых заявок
• Просмотр статуса ваших заявок
• Получение уведомлений об изменениях

<b>Команды:</b>
/start - Главное меню
/help - Эта справка

По вопросам обращайтесь в IT отдел."""
        
        await max_bot_service.send_message(chat_id, text)
        
        return {"status": "ok"}
    
    async def notify_ticket_update(
        self,
        chat_id: str,
        ticket_id: int,
        new_status: str,
        comment: str = ""
    ):
        """Notify user about ticket update"""
        text = f"""🔔 <b>Обновление заявки #{ticket_id}</b>

Новый статус: <b>{new_status}</b>"""
        
        if comment:
            text += f"\n\nКомментарий: {comment}"
        
        await max_bot_service.send_message(chat_id, text)
    
    async def setup_webhook(self) -> bool:
        """Setup webhook with MAX API"""
        webhook_url = f"{self.base_url}{self.webhook_path}"
        
        try:
            session = await max_bot_service.get_session()
            
            url = f"{max_bot_service.base_url}/setWebhook"
            payload = {"url": webhook_url}
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    print(f"Webhook установлен: {webhook_url}")
                    return True
                print(f"Ошибка установки webhook: {response.status}")
                return False
        except Exception as e:
            print(f"Error setting up webhook: {e}")
            return False
    
    def create_app(self) -> web.Application:
        """Create aiohttp web application for webhook"""
        app = web.Application()
        app.router.add_post(self.webhook_path, self.handle_webhook)
        return app


# Create bot instance
max_bot = MAXBot()
