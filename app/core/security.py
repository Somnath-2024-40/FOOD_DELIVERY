"""
core/security.py
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

from core.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ── Password ──────────────────────────────────────────────────────────────────

def get_password_hash(password: str) -> str:          
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool: 
    return pwd_context.verify(plain, hashed)


# ── Tokens ────────────────────────────────────────────────────────────────────

def _create_token(subject: Any, expires_delta: timedelta, token_type: str) -> str:
    payload = {
        "sub": str(subject),
        "exp": datetime.now(timezone.utc) + expires_delta, 
        "type": token_type,                                  
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(subject: Any) -> str:         
    return _create_token(
        subject,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        "access_token",                                
    )


def create_refresh_token(subject: Any) -> str:         
    return _create_token(
        subject,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        "refresh_token",                               
    )


def decode_token(token: str) -> Optional[dict]:      
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except PyJWTError:
        return None