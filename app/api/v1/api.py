from fastapi import APIRouter
from api.v1.endpoints import auth, users, restaurant, menu, order

api_router = APIRouter()

api_router.include_router(auth.router,        prefix="/auth",        tags=["Auth"])
api_router.include_router(users.router,       prefix="/users",       tags=["Users"])
api_router.include_router(restaurant.router,  prefix="/restaurants", tags=["Restaurants"])
api_router.include_router(menu.router,        prefix="/menus",       tags=["Menus"])
api_router.include_router(order.router,        prefix="/orders",      tags=["Orders"])