from typing import AsyncGenerator,Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from fastapi import Depends, HTTPException, status      
from sqlalchemy.future import select
from fastapi.security import OAuth2PasswordBearer

from core.config import settings
from db.base import Base
from db.session import sessionlocal
from models.user import User,UserRole
from core.security import decode_token, verify_password, get_password_hash, create_access_token


Oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_db() ->AsyncGenerator[AsyncSession,None]:
    async with sessionlocal() as db:
        try:
            yield db   
            await db.commit()
        except:
            await db.rollback()
            raise


DB = Annotated[AsyncSession,Depends(get_db)]

async def get_current_user(db:DB,token:Annotated[str,Depends(Oauth2_scheme)]) ->User:
    credentials_exception = HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate credentials",
    )

    payload = decode_token(token)
    if payload is None or payload.get("type") != "access_token":
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
        
    query = select(User).where(User.id == int(user_id))
    result = await db.execute(query)
    user = result.scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user:Annotated[User,Depends(get_current_user)] 

)-> User:

    if current_user.is_active is False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Inactive user")
    return current_user

async def get_restaurant_owner(current_user:Annotated[User,Depends(get_current_active_user)]) ->User:
    if current_user.role not in (UserRole.OWNER,UserRole.ADMIN):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
    )
    return current_user

async def admin_user(current_user:Annotated[User,Depends(get_current_active_user)]) ->User:
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
    )
    return current_user


