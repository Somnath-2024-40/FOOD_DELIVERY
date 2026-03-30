from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import datetime

from models.user import UserRole

class UserBase(BaseModel):
    email:EmailStr
    full_name:str
    phone:Optional[str]=None
    address:Optional[str]=None
    role:UserRole = UserRole.CUSTOMER


class UserCreate(UserBase):
    password:str


class UserUpdate(UserBase):
    full_name:Optional[str]=None
    phone:Optional[str]=None
    address:Optional[str]=None
    password:Optional[str]=None


class UserAdminUpdate(UserUpdate):
    is_active:Optional[bool]=None
    role:Optional[UserRole]=None

class UserResponse(BaseModel):
    id:int
    is_active:bool
    created_at:datetime

    model_config = {
        "from_attributes":True
    }

class UserPublic(BaseModel):
    id:int
    full_name:str
    role:UserRole

    model_config = {
        "from_attributes":True
    }
