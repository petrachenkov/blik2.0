from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.services import TicketService, UserService, AdminService
from backend.models.ticket import TicketStatus, Priority

router = APIRouter(prefix="/tickets", tags=["Tickets"])


class TicketCreateRequest(BaseModel):
    subject: str
    description: str


class TicketResponse(BaseModel):
    id: int
    subject: str
    description: str
    status: str
    priority: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("/create")
async def create_ticket(
    request: TicketCreateRequest,
    telegram_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Create a new ticket from messenger"""
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    ticket_service = TicketService(db)
    ticket = await ticket_service.create_ticket(
        user_id=user.id,
        subject=request.subject,
        description=request.description
    )
    
    return {
        "success": True,
        "ticket_id": ticket.id,
        "message": f"Заявка #{ticket.id} создана"
    }


@router.get("/my-tickets")
async def get_my_tickets(
    telegram_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all tickets for current user"""
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    
    ticket_service = TicketService(db)
    tickets = await ticket_service.get_user_tickets(user.id)
    
    return {
        "tickets": [
            {
                "id": t.id,
                "subject": t.subject,
                "status": t.status.value,
                "priority": t.priority.value,
                "created_at": t.created_at.isoformat()
            }
            for t in tickets
        ]
    }


@router.get("/{ticket_id}")
async def get_ticket(
    ticket_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get ticket by ID"""
    ticket_service = TicketService(db)
    ticket = await ticket_service.get_ticket(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    return {
        "id": ticket.id,
        "subject": ticket.subject,
        "description": ticket.description,
        "status": ticket.status.value,
        "priority": ticket.priority.value,
        "created_at": ticket.created_at.isoformat(),
        "assigned_admin": ticket.assigned_admin.ad_full_name if ticket.assigned_admin else None
    }
