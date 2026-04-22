import asyncio
import aiohttp
from backend.config.settings import settings


class MAXBotService:
    """Service for interacting with MAX Messenger API"""
    
    def __init__(self):
        self.base_url = "https://max-api.example.com"  # Replace with actual MAX API URL
        self.bot_token = settings.MAX_BOT_TOKEN
        self.session = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.bot_token}"}
            )
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def send_message(self, chat_id: str, text: str) -> bool:
        """Send message to user in MAX messenger"""
        try:
            session = await self.get_session()
            
            # MAX API endpoint - adjust based on actual API documentation
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }
            
            async with session.post(url, json=payload) as response:
                if response.status == 200:
                    return True
                print(f"Failed to send message: {response.status}")
                return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False
    
    async def send_keyboard(self, chat_id: str, text: str, buttons: list[list[str]]) -> bool:
        """Send message with inline keyboard"""
        try:
            session = await self.get_session()
            
            url = f"{self.base_url}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": text,
                "reply_markup": {
                    "inline_keyboard": [
                        [{"text": btn, "callback_data": btn.lower().replace(" ", "_")} for btn in row]
                        for row in buttons
                    ]
                }
            }
            
            async with session.post(url, json=payload) as response:
                return response.status == 200
        except Exception as e:
            print(f"Error sending keyboard: {e}")
            return False
    
    async def edit_message(self, chat_id: str, message_id: str, text: str) -> bool:
        """Edit existing message"""
        try:
            session = await self.get_session()
            
            url = f"{self.base_url}/editMessageText"
            payload = {
                "chat_id": chat_id,
                "message_id": message_id,
                "text": text
            }
            
            async with session.post(url, json=payload) as response:
                return response.status == 200
        except Exception as e:
            print(f"Error editing message: {e}")
            return False
    
    async def get_user_info(self, user_id: str) -> dict | None:
        """Get user information from MAX"""
        try:
            session = await self.get_session()
            
            url = f"{self.base_url}/getUser/{user_id}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None


max_bot_service = MAXBotService()
