from __future__ import annotations

from typing import Annotated, Optional,Any

from fastapi import APIRouter, Depends, Query, status

from core.dependencies import DB, get_current_active_user, get_restaurant_owner  
from utils.pagination import PaginateResponse, paginationDep, make_paginated_response  
from schemas.restaurant import (
    RestaurantCreate,
    RestaurantUpdate,
    RestaurantResponse,
    RestaurantListResponse,
)
import services.restaurant as restaurant_service



router = APIRouter(prefix="/restaurants", tags=["restaurants"])

@router.post("/",response_model = PaginateResponse[RestaurantResponse],status_code=status.HTTP_201_CREATED)
async def create_restaurant(
    restaurant_in:RestaurantCreate,
    db:DB,
    current_user=Depends(get_current_active_user)
):
    return await restaurant_service.create_restaurant(db,current_user,restaurant_in)

@router.get("/", response_model=PaginateResponse[RestaurantListResponse])
async def list_restaurants(
    db: DB,
    pagination: paginationDep,
    cuisine_type: Optional[str] = Query(None),
    restaurant_status: Optional[RestaurantStatus] = Query(None),
):
    restaurants, total = await restaurant_service.list_restaurants(
        db,
        cuisine_type=cuisine_type,
        restaurant_status=restaurant_status,
        **pagination.to_dict()          
    )
    return make_paginated_response(restaurants, total, pagination)


@router.get("/{restaurant_id}",response_model = RestaurantResponse)
async def update_restaurant(
    restaurant_id:int,
    data:RestaurantUpdate,
    db:DB,
    current_user=Depends(get_restaurant_owner)
):
    restaurant = await restaurant_service.get_restaurant_or_404(db,restaurant_id)
    return await restaurant_service.update_restaurant(db,restaurant,data,current_user)


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_restaurant(                                      # ✅ async
    restaurant_id: int,
    db: DB,
    owner=Depends(get_restaurant_owner),
):
    restaurant = await restaurant_service.get_restaurant_or_404(db, restaurant_id)
    await restaurant_service.delete_restaurant(db, restaurant, owner)