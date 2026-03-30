from __future__ import annotations

from sqlalchemy import func , select
from typing import Optional,Tuple,List
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status as http_status

from models.restaurant import Restaurant,RestaurantStatus
from models.menu import MenuItem,MenuCategory
from models.user import User
from schemas.restaurant import RestaurantCreate,RestaurantUpdate
from schemas.menu import MenuItemCreate

MAX_PAGE_SIZE = 100

# ____helpers_____

def _clamp_page_size(page_size:int)->int:
    return max(1,min(page_size,MAX_PAGE_SIZE))

async def _count(db:AsyncSession,base_query)->int:
    Query = select(func.count()).selectinload(base_query.subquery())
    result =  await db.execute(Query)
    return result.scalar_one()

def _assert_owner_or_admin(restaurant:Restaurant,user:User)->None:
    if user.Role == UserRole.ADMIN:
        return
    if restaurant.owner_id != user.id:
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform requested action",
        )

# ----------------------

async def get_restaurant(
    db:AsyncSession,
    restaurant_id:int
)->Optional[Restaurant]:

    Query = select(Restaurant).where(Restaurant.id == restaurant_id,Restaurant.is_active.is_(True))
    result = await db.execute(Query)
    return result.scalar_one_or_none()

async def get_restaurant_or_404(db:AsyncSession,restaurant_id:int)->Restaurant:
    restaurant = await get_restaurant(db,restaurant_id)
    if not restaurant:
        raise HTTPException(
            status_code = http_status.HTTP_404_NOT_FOUND,
            detail = "Restaurant not found"
        )
    return restaurant

async def list_restaurant(
    db:AsyncSession,
    page:int = 1,
    page_size:int = 10,
    restaurant_status:Optional[RestaurantStatus] = None
)->Tuple[List[Restaurant],int]:

    page_size = await _clamp_page_size(page_size)

    base = select(Restaurant).where(Restaurant.is_active.is_(True))

    if cuisine_type is not None and cuisine_type.strip():
        base = base.where(Restaurant.cuisine_type.ilike(f"%{cuisine_type.strip()}%"))
    if restaurant_status is not None:
        base = base.where(Restaurant.status == restaurant_status)
    
    total = await _count(db,base)
    result = await db.execute(base.offset((page-1)*page_size).limit(page_size))
    return result.scalars().all(),total

async def create_restaurant(
    db:AsyncSession,
    restaurant_in:RestaurantCreate,
    owner:User
)->Restaurant:

    restaurant = Restaurant(**restaurant_in.dict(),owner_id = owner.id)
    try:
        db.add(restaurant)
        await db.commit()
        await db.refresh(restaurant)
    except Exception:
        await db.rollback()
        raise
    return restaurant

async def update_restaurant(
    db:AsyncSession,
    restaurant:Restaurant,
    restaurant_in:RestaurantUpdate,
    restaurant_id:int,
    owner:User
)->Restaurant:

    _assert_owner_or_admin(restaurant,owner)

    restaurant = await get_restaurant_or_404(db,restaurant_id)
    
    for field,value in restaurant_in.dump(exclude_unset = True).items():
        setattr(restaurant,field,value)  #setattr(object, "attribute_name", value) --->this is the formula for setting attrubutes .. and setattr is change the value dynamically
    
    try:
        await db.commit()
        await db.refresh(restaurant)
    except Exception:
        await db.rollback()
        raise
    return restaurant

async def delete_restaurant(
    db:AsyncSession,
    restaurant_id:int,
    restaurant:Restaurant,
    owner:User
) ->None:

    _assert_owner_or_admin(restaurant,owner)

    restaurant = await get_restaurant_or_404(db,restaurant_id)
    restaurant.is_active = False 

    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise


async def get_menu_item(
    db:AsyncSession,
    item_id:int
)->optional[MenuItem]:

    Query = select(MenuItem).where(MenuItem.id == item_id).options(selectinload(MenuItem.restaurant))
    result = await db.execute(Query)
    return result.scalar_one_or_none()

async def get_menu_item_or_404(
    db:AsyncSession,
    item_id:int
)->MenuItem:

    item = await get_menu_item(db,item_id)
    if not item:
        raise HTTPException(
        status_code = http_status.HTTP_404_NOT_FOUND,
        detail = "Menu item not found"
        )
    return item


async def list_menu(
    db:ASyncSession,
    restaurant_id:int,
    page:int = 1,
    page_size:int = 10,
    only_available:bool = False,
    
) -> Tuple[List[MenuItem],int]:

    page_size = await _clamp_page_size(page_size)

    base = select(MenuItem).where(MenuItem.restaurant.id == restaurant_id)

    if only_available:
        base = base.where(MenuItem.is_available.is_(True))
    
    total = await _count(db,base)
    result = await db.execute(base.offset((page-1)*page_size).limit(page_size))
    return result.scalars().all(),total



async def create_menu(
    db:AsyncSession,
    restaurant : Restaurant,
    menu_item_in:MenuItemCreate,
    requester:User
) ->MenuItem:

    _assert_owner_or_admin(restaurant,requester)

    menu_item = MenuItem(**menu_item_in.dict(), restaurant_id=restaurant.id)

    try:
        db.add(menu_item)
        await db.commit()
        await db.refresh(menu_item)
    except Exception:
        await db.rollback()
        raise
    return menu_item

async def update_menu(
    db:AsyncSession,
    requester:User,
    restaurant:Restaurant,
    menu_item:MenuItem,
    menu_item_in:MenuItemUpdate
) -> MenuItem:

    _assert_owner_or_admin(restaurant,requester)

    for field,value in menu_item_in.dump(exclude_unset = True).items():
        setattr(menu_item,field,value)  #setattr(object, "attribute_name", value) --->this is the formula for setting attrubutes .. and setattr is change the value dynamically
    
    try:
        await db.commit()
        await db.refresh(menu_item)
    except Exception:
        await db.rollback()
        raise
    return menu_item


async def delete_menu(
    db:AsyncSession,
    requester:User,
    item:ItemMenu
) ->None:

    _assert_owner_or_admin(restaurant,requester)

    item.is_available = False

    try:
        
        await db.commit()
    except Exception:
        await db.rollback()
        raise




