from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database import get_db
from backend.services import ad_auth_service, UserService, AdminService
from backend.models.ticket import User as UserModel

router = APIRouter(prefix="/auth", tags=["Authentication"])


class ADLoginRequest(BaseModel):
    username: str
    password: str
    telegram_id: str


class ADLoginResponse(BaseModel):
    success: bool
    message: str
    user_id: int | None = None


@router.post("/ad-login", response_model=ADLoginResponse)
async def ad_login(request: ADLoginRequest, db: AsyncSession = Depends(get_db)):
    """
    Authenticate user via Active Directory and link to Telegram account.
    This is called once during initial setup.
    """
    # Authenticate against AD
    ad_user = ad_auth_service.authenticate(request.username, request.password)
    
    if not ad_user:
        return ADLoginResponse(
            success=False,
            message="Неверное имя пользователя или пароль"
        )
    
    user_service = UserService(db)
    
    # Check if user already exists
    existing_user = await user_service.get_by_ad_username(ad_user['username'])
    
    if existing_user:
        # Update telegram_id if needed
        if existing_user.telegram_id != request.telegram_id:
            await user_service.link_telegram_to_user(existing_user, request.telegram_id)
        return ADLoginResponse(
            success=True,
            message=f"Добро пожаловать, {existing_user.ad_full_name}!",
            user_id=existing_user.id
        )
    
    # Create new user
    new_user = await user_service.create_user(
        telegram_id=request.telegram_id,
        ad_username=ad_user['username'],
        ad_full_name=ad_user['full_name'],
        ad_email=ad_user['email'],
        ad_department=ad_user['department']
    )
    
    return ADLoginResponse(
        success=True,
        message=f"Аккаунт создан. Добро пожаловать, {new_user.ad_full_name}!",
        user_id=new_user.id
    )


@router.get("/check-user/{telegram_id}")
async def check_user(telegram_id: str, db: AsyncSession = Depends(get_db)):
    """Check if user is already registered"""
    user_service = UserService(db)
    user = await user_service.get_by_telegram_id(telegram_id)
    
    if not user:
        return {"registered": False, "message": "Пользователь не найден"}
    
    return {
        "registered": True,
        "user_id": user.id,
        "username": user.ad_username,
        "full_name": user.ad_full_name
    }
