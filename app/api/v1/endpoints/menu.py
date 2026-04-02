from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, status,UploadFile, Form, Depends,File
from fastapi import Depends

from core.dependencies import DB, get_restaurant_owner 
from models.enums import MenuCategory 
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

@router.post("/restaurant/{restaurant_id}/menu/items",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_menu_item(
    restaurant_id: int,


    image: Annotated[UploadFile, File(...)],
    
    db: Annotated[DB, Depends()],
    current_user: Annotated[User, Depends(get_restaurant_owner)],

    name: Annotated[str, Form(...)],
    description: Annotated[str, Form(...)],
    price: Annotated[float, Form(...)],
    category: Annotated[MenuCategory, Form()]=MenuCategory.OTHER,
    is_available: Annotated[bool, Form()]=True,
    is_vegetarian: Annotated[bool, Form()]=False,
    is_vegan: Annotated[bool, Form()]=False,
    calories: Annotated[Optional[int], Form()]=None,
    preparation_time: Annotated[Optional[int], Form()]=None,

):
    item_in = MenuItemCreate(
        name=name,
        description=description,
        price=price,
        category=category,
        is_available=is_available,
        is_vegetarian=is_vegetarian,
        is_vegan=is_vegan,
        calories=calories,
        preparation_time=preparation_time
    )
    restaurant = await restaurant_service.get_restaurant_or_404(db, restaurant_id)

    return await restaurant_service.create_menu(
        db, restaurant, item_in, image, current_user
    )

@router.delete("/menu/{item_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_item(
    restaurant_id:int,
    item_id:int,
    db:DB,
    current_user=Depends(get_restaurant_owner)
):
    menu_item = await restaurant_service.get_menu_item_or_404(db,item_id)
    await restaurant_service.delete_menu(db,current_user,menu_item) 
