

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from models.menu import MenuCategory 

class MenuItemBase(BaseModel):
    
    name:str
    description:str
    price:float
    image_url:Optional[str]=None
    category:MenuCategory = MenuCategory.OTHER
    is_available:bool = True
    is_vegetarian:bool = False
    is_vegan:bool = False
    calories:Optional[int] = None
    preparation_time:Optional[int] = None

class MenuItemCreate(MenuItemBase):
    pass


class MenuItemUpdate(BaseModel):
    name:Optional[str]=None
    description:Optional[str]=None
    price:Optional[float]=None
    category:Optional[MenuCategory]=None
    is_available:Optional[bool]=None
    is_vegetarian:Optional[bool]=None
    is_vegan:Optional[bool]=None
    calories:Optional[int]=None
    preparation_time:Optional[int]=None


class MenuItemResponse(MenuItemBase):
    id:int
    restaurant_id:int
    created_at:datetime

    model_config = {
        "from_attributes":True
    }