from pydantic import BaseModel, EmailStr, Field
from fastapi import Form
from typing import Optional
from datetime import datetime
from models.enums import RestaurantStatus 

# --- Base Schema (Shared fields) ---
from pydantic import BaseModel, EmailStr
from fastapi import Form
from typing import Optional
from datetime import datetime
from models.enums import RestaurantStatus 

# --- Base Schema ---
class RestaurantBase(BaseModel):
    # 1. Define fields here so Pydantic recognizes them
    name: str
    address: str
    description: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    cuisine_type: Optional[str] = None
    min_order_price: float = 0.0
    delivery_fee: float = 0.0
    estimated_delivery_time: int = 30

    @classmethod    
    def as_form(
        cls,
        name: str = Form(...),
        address: str = Form(...),
        description: Optional[str] = Form(None),
        phone_number: Optional[str] = Form(None),
        email: Optional[EmailStr] = Form(None),
        cuisine_type: Optional[str] = Form(None),
        min_order_price: float = Form(0.0),
        delivery_fee: float = Form(0.0),
        estimated_delivery_time: int = Form(30)
    ):
        return cls(
            name=name,
            address=address,
            description=description,
            phone_number=phone_number,
            email=email,
            cuisine_type=cuisine_type,
            min_order_price=min_order_price,
            delivery_fee=delivery_fee,
            estimated_delivery_time=estimated_delivery_time
        )

# --- Create Schema ---
class RestaurantCreate(RestaurantBase):
    pass

# --- Update Schema ---
class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    image_url: Optional[str] = None
    cuisine_type: Optional[str] = None
    min_order_price: Optional[float] = None
    delivery_fee: Optional[float] = None
    estimated_delivery_time: Optional[int] = None
    status: Optional[str] = None

# --- Full Detail Response ---
class RestaurantResponse(RestaurantBase):
    id: int
    rating: float
    total_ratings: int


   

    
    status: RestaurantStatus
    image_url: str
    is_active: bool
    owner_id: int
    created_at: datetime

    model_config = {
        "from_attributes": True
    }

# --- List/Feed Response ---
class RestaurantListResponse(BaseModel):
    id: int
    name: str
    address: str
    description: Optional[str] = None
    cuisine_type: Optional[str] = None
    rating: float
    delivery_fee: float
    estimated_delivery_time: int
    status: RestaurantStatus
    image_url: Optional[str] = None
    is_active: bool

    model_config = {
        "from_attributes": True
    }


# At the very bottom of your restaurant schema file
RestaurantCreate.model_rebuild()