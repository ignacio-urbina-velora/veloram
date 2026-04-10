"""Auth service – JWT tokens + password hashing."""

from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models.user import User
from app.models.affiliate import Affiliate


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int) -> str:
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])


async def register_user(db: AsyncSession, email: str, username: str, password: str) -> User:
    # Check email uniqueness
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalar_one_or_none():
        raise ValueError("Email already registered")

    # Check username uniqueness
    existing = await db.execute(select(User).where(User.username == username))
    if existing.scalar_one_or_none():
        raise ValueError("Username already taken")

    user = User(
        email=email,
        username=username,
        hashed_password=hash_password(password),
        credits=settings.FREE_CREDITS,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    # Create affiliate record automatically
    affiliate = Affiliate(
        user_id=user.id,
        code=username.lower().replace(" ", "_"),  # Generate unique-ish code from username
        is_active=True
    )
    db.add(affiliate)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("USER_NOT_FOUND")
    if not verify_password(password, user.hashed_password):
        raise ValueError("INVALID_PASSWORD")
    return user


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def authenticate_user_by_token(db: AsyncSession, email: str, token: str) -> User:
    # For magic links, we verify that the token is a valid JWT signed with our secret
    try:
        payload = decode_token(token)
        if payload.get("email") != email:
            raise ValueError("Token email mismatch")
        
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        if not user:
            raise ValueError("USER_NOT_FOUND")
        return user
    except Exception as e:
        raise ValueError(f"INVALID_TOKEN: {str(e)}")
