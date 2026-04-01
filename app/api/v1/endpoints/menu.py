from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, status
from fastapi import Depends

from core.dependencies import DB, get_restaurant_owner  
from models.menu import MenuItem    
from models.user import User                                
from utils.pagination import paginationDep, make_paginated_response, PaginateResponse
from schemas.menu import MenuItemCreate, MenuItemUpdate, MenuItemResponse  
import services.restaurant as restaurant_service



router = APIRouter()

@router.get("/restaurant/{restaurant_id}/menu/items",response_model=PaginateResponse[MenuItemResponse])
async def list_menu_items(
    restaurant_id:int,
    db:DB,
    pagination:paginationDep,

):
    await restaurant_service.get_restaurant_or_404(db,restaurant_id)
    items, total = await restaurant_service.list_menu(db,restaurant_id,pagination.page,pagination.page_size)
    return make_paginated_response(items,total,pagination)

@router.post("/restaurant/{restaurant_id}/menu/items",response_model=MenuItemResponse,status_code=status.HTTP_201_CREATED)
async def create_menu_item(
    restaurant_id:int,
    item_in:MenuItemCreate,
    db:DB,
    current_user=Depends(get_restaurant_owner)
): 
    restaurant = await restaurant_service.get_restaurant_or_404(db,restaurant_id)
    return await restaurant_service.create_menu(db,restaurant,item_in,current_user)

@router.delete("/menu/{item_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    restaurant_id:int,
    item_id:int,
    db:DB,
    current_user=Depends(get_restaurant_owner)
):
    menu_item = await restaurant_service.get_menu_item_or_404(db,item_id)
    await restaurant_service.delete_menu(db,current_user,menu_item) 
