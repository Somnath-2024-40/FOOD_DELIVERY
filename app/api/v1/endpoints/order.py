from typing import Annotated,Any

from fastapi import APIRouter, Depends, status

from core.dependencies import DB, get_current_active_user, admin_user 
from models.user import User
from utils.pagination import PaginateResponse, paginationDep, make_paginated_response  
from schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderSummary,
    OrderStatusUpdate,
    OrderAssignDelivery,
)
import services.order as order_service 




router = APIRouter()

@router.post("/",response_model = OrderResponse,status_code=status.HTTP_201_CREATED)
async def create_order(
    order_in:OrderCreate,
    db:DB,
    current_user=Depends(get_current_active_user)
):
    return await order_service.create_order(db,order_in,current_user)

@router.get("/my",response_model = PaginateResponse[OrderSummary])
async def get_my_orders(
    db:DB,
    pagination:paginationDep,
    current_user=Depends(get_current_active_user),
    
):
    orders,total = await order_service.list_order_for_customers(db,current_user.id,**pagination.to_dict())
    return make_paginated_response(orders,total,pagination)

@router.get("/restaurant/{restaurant_id}",response_model = PaginateResponse[OrderSummary])
async def get_restaurant_orders(
    restaurant_id:int,
    db:DB,
    pagination:paginationDep,
    current_user=Depends(admin_user),
    
):
    orders,total = await order_service.List_order_for_restaurant(db,restaurant_id,**pagination.to_dict())
    return make_paginated_response(orders,total,pagination)


@router.get("/all",response_model = PaginateResponse[OrderSummary])
async def get_all_orders(
    db:DB,
    pagination:paginationDep,
    current_user=Depends(admin_user),
    
):
    orders,total = await order_service.list_all_orders(db,**pagination.to_dict())
    return make_paginated_response(orders,total,pagination)

@router.patch("/{order_id}/status",response_model = OrderResponse)
async def update_order_status(
    db:DB,
    order_id:int,
    status_update:OrderStatusUpdate,
    current_user=Depends(admin_user)
):
    order = await order_service.get_order_or_404(db,order_id) 
    return await order_service.update_order_status(db,order,status_update.status)


@router.get("/{order_id}",response_model = OrderResponse)
async def get_order(
    db:DB,
    order_id:int,
    current_user=Depends(get_current_active_user)
):
    return await order_service.get_order(db,order_id)


@router.patch("/{order_id}/assign-delivery",response_model = OrderResponse)
async def assign_delivery_person(
    db:DB,
    order_id:int,
    assign_info:OrderAssignDelivery,
    current_user=Depends(admin_user)
):
    order = await order_service.get_order_or_404(db,order_id)
    return await order_service.assign_delivery_agent(db,order,assign_info.delivery_agent_id,current_user)

