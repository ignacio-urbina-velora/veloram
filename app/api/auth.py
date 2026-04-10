"""Auth endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from sqlalchemy import select
from app.models.user import User
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse, ForgotPasswordRequest, LoginTokenRequest
from app.services.auth_service import (
    register_user, authenticate_user, create_access_token, create_refresh_token,
    decode_token, get_user_by_id,
)
from app.config import settings
from app.api.deps import get_current_user
from app.services.email_service import email_service
import asyncio

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, req.email, req.username, req.password)
        # Send welcome email in background
        asyncio.create_task(email_service.send_welcome_email(user.email, user.username))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    try:
        user = await authenticate_user(db, req.email, req.password)
    except ValueError as e:
        detail = str(e)
        status_code = status.HTTP_401_UNAUTHORIZED
        if detail == "USER_NOT_FOUND":
            # Optional: depending on security preferences, we might want to keep it vague, 
            # but user expressly requested "email doesn't exist" feedback.
            pass
        raise HTTPException(status_code=status_code, detail=detail)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/login-token", response_model=TokenResponse)
async def login_token(req: LoginTokenRequest, db: AsyncSession = Depends(get_db)):
    from app.services.auth_service import authenticate_user_by_token
    try:
        user = await authenticate_user_by_token(db, req.email, req.token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise ValueError("Not a refresh token")
        user_id = int(payload["sub"])
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user = await get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    # Check if user exists
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    
    if user:
        # For now, we simulate a reset link pointing to the frontend
        reset_link = f"{settings.APP_URL}/reset-password?token=mock-token-{user.id}"
        asyncio.create_task(email_service.send_password_reset_email(user.email, reset_link))
    
    return {"message": "Si el correo está registrado, recibirás un enlace de recuperación."}


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return user
