
from fastapi import Depends, UploadFile
from pydantic import BaseModel
from typing import Annotated
from typing import Optional
from datetime import datetime
from fastapi import Form,File, UploadFile

from models.menu import MenuCategory 

class MenuItemBase(BaseModel):
    name: str
    description: str
    price: float
    image_url: Optional[str] = None
    category: MenuCategory = MenuCategory.OTHER
    is_available: bool = True
    is_vegetarian: bool = False
    is_vegan: bool = False
    calories: Optional[int] = None
    preparation_time: Optional[int] = None

    # @classmethod
    # def as_form(
    #     cls,
    #     name: str = Form(...),
    #     description: str = Form(...),
    #     price: float = Form(...),
    #     category: MenuCategory = Form(MenuCategory.OTHER),
    #     is_available: bool = Form(True),
    #     is_vegetarian: bool = Form(False),
    #     is_vegan: bool = Form(False),
    #     calories: Optional[int] = Form(None),
    #     preparation_time: Optional[int] = Form(None),
    # ):
    #     return cls(
    #         name=name,
    #         description=description,
    #         price=price,
    #         category=category,
    #         is_available=is_available,
    #         is_vegetarian=is_vegetarian,
    #         is_vegan=is_vegan,
    #         calories=calories,
    #         preparation_time=preparation_time
    #     )


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
    image_url: str
    model_config = {
        "from_attributes":True
    }


MenuItemCreate.model_rebuild()
MenuItemResponse.model_rebuild()