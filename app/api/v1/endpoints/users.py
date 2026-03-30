"""
routers/users.py
"""
from __future__ import annotations

from typing import Annotated,Any

from fastapi import APIRouter, Depends, status

from core.dependencies import DB, get_current_active_user, admin_user 
from models.user import User
from utils.pagination import PaginateResponse, paginationDep, make_paginated_response
from schemas.user import UserResponse, UserUpdate, UserAdminUpdate
import services.user as user_service


router = APIRouter(prefix="/users", tags=["users"])               


@router.get("/", response_model=PaginateResponse[UserResponse])
async def list_users(                                            
    pagination: paginationDep,                                   
    db: DB,
    current_user=Depends(admin_user),      
):
    items, total = await user_service.get_users(db, **pagination.to_dict())  
    return make_paginated_response(items, total, pagination)     


@router.get("/me", response_model=UserResponse)
async def get_me(                                                
    current_user=Depends(get_current_active_user),
):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_me(                                             
    user_in: UserUpdate,
    db: DB,
    current_user=Depends(get_current_active_user),
):
    return await user_service.update_user(db, current_user, user_in, current_user)  


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(                                              
    user_id: int,
    db: DB,
    current_user=Depends(admin_user),      
):
    return await user_service.get_user_or_404(db, user_id)       


@router.patch("/{user_id}", response_model=UserResponse)
async def admin_update_user(                                     
    user_id: int,
    user_in: UserAdminUpdate,
    db: DB,
    current_user=Depends(admin_user),      
):
    user = await user_service.get_user_or_404(db, user_id)       
    return await user_service.admin_update_user(db, user, user_in, current_user)  

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(                                          
    user_id: int,
    db: DB,
    current_user= Depends(admin_user),     
):
    user = await user_service.get_user_or_404(db, user_id)      
    await user_service.delete_user(db, user)                    