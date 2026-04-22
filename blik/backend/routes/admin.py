from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.services import TicketService, UserService, AdminService
from backend.models.ticket import TicketStatus, Priority

router = APIRouter(prefix="/admin/tickets", tags=["Admin Tickets"])
security = HTTPBearer()


class TicketUpdateRequest(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_admin_id: Optional[int] = None


class TicketListItem(BaseModel):
    id: int
    subject: str
    description: str
    status: str
    priority: str
    user_name: str
    assigned_admin_name: Optional[str]
    created_at: str
    
    class Config:
        from_attributes = True


async def verify_admin(
    credentials: HTTPAuthorizationCredentials = Security(security),
    db: AsyncSession = Depends(get_db)
):
    """Verify admin token (simplified - in production use JWT)"""
    # TODO: Implement proper JWT verification
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return token


@router.get("/")
async def get_all_tickets(
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """Get all tickets for admin panel"""
    ticket_service = TicketService(db)
    tickets = await ticket_service.get_all_tickets()
    
    return {
        "tickets": [
            {
                "id": t.id,
                "subject": t.subject,
                "description": t.description[:100] + "..." if len(t.description) > 100 else t.description,
                "status": t.status.value,
                "priority": t.priority.value,
                "user_name": t.user.ad_full_name or t.user.ad_username,
                "assigned_admin_name": t.assigned_admin.ad_full_name if t.assigned_admin else None,
                "created_at": t.created_at.isoformat(),
                "user_email": t.user.ad_email
            }
            for t in tickets
        ]
    }


@router.get("/open")
async def get_open_tickets(
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """Get only open tickets"""
    ticket_service = TicketService(db)
    tickets = await ticket_service.get_open_tickets()
    
    return {
        "tickets": [
            {
                "id": t.id,
                "subject": t.subject,
                "status": t.status.value,
                "priority": t.priority.value,
                "user_name": t.user.ad_full_name or t.user.ad_username,
                "created_at": t.created_at.isoformat()
            }
            for t in tickets
        ]
    }


@router.put("/{ticket_id}")
async def update_ticket(
    ticket_id: int,
    request: TicketUpdateRequest,
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """Update ticket (assign, change priority, change status)"""
    ticket_service = TicketService(db)
    ticket = await ticket_service.get_ticket(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Заявка не найдена")
    
    # Update status
    if request.status:
        try:
            status = TicketStatus(request.status)
            await ticket_service.update_ticket_status(ticket, status)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {request.status}")
    
    # Update priority
    if request.priority:
        try:
            priority = Priority(request.priority)
            await ticket_service.update_ticket_priority(ticket, priority)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid priority: {request.priority}")
    
    # Assign admin
    if request.assigned_admin_id is not None:
        await ticket_service.assign_ticket(ticket, request.assigned_admin_id)
    
    return {
        "success": True,
        "message": "Заявка обновлена",
        "ticket_id": ticket.id
    }


@router.get("/admins")
async def get_admins(
    db: AsyncSession = Depends(get_db),
    admin_token: str = Depends(verify_admin)
):
    """Get list of all admins for assignment"""
    admin_service = AdminService(db)
    admins = await admin_service.get_all_admins()
    
    return {
        "admins": [
            {
                "id": a.id,
                "username": a.ad_username,
                "full_name": a.ad_full_name,
                "email": a.ad_email
            }
            for a in admins
        ]
    }
