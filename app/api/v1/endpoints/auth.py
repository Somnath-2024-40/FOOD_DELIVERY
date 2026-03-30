from __future__ import annotations


import logging
from typing import Annotated,Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies import DB, get_current_active_user  
from core.security import create_access_token, create_refresh_token, decode_token
from models.user import User
from schemas.auth import RefreshTokenRequest, Token
from schemas.user import UserCreate, UserResponse            
import services.user as user_service




logger = logging.getLogger(__name__)
router = APIRouter()

def _401(detail:str = "Unauthorized")->HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
)

def _400(detail:str)->HTTPException:
    return HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=detail
    )

def _token_pair(user_id:int)->Token:
    access_token = create_access_token({"sub": str(user_id)})
    refresh_token = create_refresh_token({"sub": str(user_id)})
    return Token(access_token=access_token, refresh_token=refresh_token)

async def _resolve_active_user(
    db:AsyncSession,
    sub:object
)->User:
    try:
        user = await db.get(User, int(sub))
    except Exception as e:
        raise _401()
    if not user or not user.is_active:
        raise _401()
    return user



@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in:UserCreate,
    db:DB

):
    return await user_service.create_user(db,user_in)

@router.post("/login", response_model=Token)
async def Login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DB
):
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise _401("Invalid username or password")
    return _token_pair(user.id)

@router.post("/refresh", response_model=Token)
async def refresh_token(
    body: RefreshTokenRequest,
    db: DB
):
    payload = decode_token(body.refresh_token)
    if not payload:
        raise _401("Invalid refresh token")
    user = await _resolve_active_user(db, payload.get("sub"))
    logger.info(f"User {user.id} refreshed token")
    return _token_pair(user.id)


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user=Depends(get_current_active_user)
):
    return current_user

    