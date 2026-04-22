from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.ticket import User, Admin, Ticket, TicketStatus, Priority
from datetime import datetime


class UserService:
    """Service for managing users"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_ad_username(self, ad_username: str) -> User | None:
        result = await self.db.execute(
            select(User).where(User.ad_username == ad_username)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self,
        telegram_id: str,
        ad_username: str,
        ad_full_name: str | None = None,
        ad_email: str | None = None,
        ad_department: str | None = None
    ) -> User:
        user = User(
            telegram_id=telegram_id,
            ad_username=ad_username,
            ad_full_name=ad_full_name,
            ad_email=ad_email,
            ad_department=ad_department
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def link_telegram_to_user(self, user: User, telegram_id: str) -> User:
        user.telegram_id = telegram_id
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def get_all_users(self) -> list[User]:
        result = await self.db.execute(select(User))
        return result.scalars().all()


class AdminService:
    """Service for managing admins"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_ad_username(self, ad_username: str) -> Admin | None:
        result = await self.db.execute(
            select(Admin).where(Admin.ad_username == ad_username)
        )
        return result.scalar_one_or_none()
    
    async def create_admin(
        self,
        ad_username: str,
        ad_full_name: str | None = None,
        ad_email: str | None = None,
        is_super_admin: bool = False
    ) -> Admin:
        admin = Admin(
            ad_username=ad_username,
            ad_full_name=ad_full_name,
            ad_email=ad_email,
            is_super_admin=is_super_admin
        )
        self.db.add(admin)
        await self.db.flush()
        await self.db.refresh(admin)
        return admin
    
    async def get_all_admins(self) -> list[Admin]:
        result = await self.db.execute(
            select(Admin).where(Admin.is_active == True)
        )
        return result.scalars().all()


class TicketService:
    """Service for managing tickets"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_ticket(
        self,
        user_id: int,
        subject: str,
        description: str,
        messenger_chat_id: str | None = None,
        messenger_message_id: str | None = None
    ) -> Ticket:
        ticket = Ticket(
            user_id=user_id,
            subject=subject,
            description=description,
            messenger_chat_id=messenger_chat_id,
            messenger_message_id=messenger_message_id
        )
        self.db.add(ticket)
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket
    
    async def get_ticket(self, ticket_id: int) -> Ticket | None:
        result = await self.db.execute(
            select(Ticket).where(Ticket.id == ticket_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_tickets(self, user_id: int) -> list[Ticket]:
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.user_id == user_id)
            .order_by(Ticket.created_at.desc())
        )
        return result.scalars().all()
    
    async def update_ticket_status(
        self,
        ticket: Ticket,
        status: TicketStatus
    ) -> Ticket:
        ticket.status = status
        if status == TicketStatus.RESOLVED:
            ticket.resolved_at = datetime.utcnow()
        elif status == TicketStatus.CLOSED:
            ticket.closed_at = datetime.utcnow()
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket
    
    async def assign_ticket(
        self,
        ticket: Ticket,
        admin_id: int | None
    ) -> Ticket:
        ticket.assigned_admin_id = admin_id
        if admin_id and ticket.status == TicketStatus.NEW:
            ticket.status = TicketStatus.IN_PROGRESS
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket
    
    async def update_ticket_priority(
        self,
        ticket: Ticket,
        priority: Priority
    ) -> Ticket:
        ticket.priority = priority
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket
    
    async def get_all_tickets(self) -> list[Ticket]:
        result = await self.db.execute(
            select(Ticket).order_by(Ticket.created_at.desc())
        )
        return result.scalars().all()
    
    async def get_open_tickets(self) -> list[Ticket]:
        result = await self.db.execute(
            select(Ticket)
            .where(Ticket.status.not_in([TicketStatus.RESOLVED, TicketStatus.CLOSED]))
            .order_by(Ticket.created_at.desc())
        )
        return result.scalars().all()
