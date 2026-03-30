from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime

from models.restaurant import RestaurantStatus

class RestaurantBase(BaseModel):
    name:str
    description:Optional[str]=None
    address:str
    phone:Optional[str]=None
    email:Optional[EmailStr]=None
    image_url:Optional[str]=None
    cuisine_type:Optional[str]=None
    min_order_price:float = 0.0
    delivery_fee:float = 0.0
    estimated_delivery_time:int = 30



class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name:Optional[str]=None
    address:Optional[str]=None
    description:Optional[str]=None
    phone:Optional[str]=None
    email:Optional[EmailStr]=None
    image_url:Optional[str]=None
    cuisine_type:Optional[str]=None
    min_order_price:Optional[float]=None
    delivery_fee:Optional[float]=None
    estimated_delivery_time:Optional[int]=None
    status:Optional[RestaurantStatus]=None


class RestaurantResponse(RestaurantBase):
    id:int
    rating:float
    total_ratings:int
    status:RestaurantStatus
    is_active:bool
    owner_id:int
    created_at:datetime


    model_config = {
        "from_attributes":True
    }


class RestaurantListResponse(BaseModel):
    id:int
    name:str
    cuisine_type:Optional[str]=None
    rating:float
    delivery_fee:float
    estimated_delivery_time:int
    status:RestaurantStatus
    image_url:Optional[str]
    model_config = {
        "from_attributes":True
    }