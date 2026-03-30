from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from models.restaurant import RestaurantStatus  
from models.enums import RestaurantStatus 

# --- Base Schema (Shared fields) ---
class RestaurantBase(BaseModel):
    name: str
    description: Optional[str] = None
    address: str
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    image_url: Optional[str] = None
    cuisine_type: Optional[str] = None
    min_order_price: float = 0.0
    delivery_fee: float = 0.0
    estimated_delivery_time: int = 30

# --- Create Schema ---
class RestaurantCreate(RestaurantBase):
    pass

# --- Update Schema ---
class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    image_url: Optional[str] = None
    cuisine_type: Optional[str] = None
    min_order_price: Optional[float] = None
    delivery_fee: Optional[float] = None
    estimated_delivery_time: Optional[int] = None
    status: Optional[RestaurantStatus] = None

# --- Full Detail Response ---
class RestaurantResponse(RestaurantBase):
    id: int
    rating: float
    total_ratings: int
    status: RestaurantStatus
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
    cuisine_type: Optional[str] = None
    rating: float
    delivery_fee: float
    estimated_delivery_time: int
    status: RestaurantStatus
    image_url: Optional[str] = None

    model_config = {
        "from_attributes": True
    }

# --- CRITICAL: Rebuild models to resolve forward references ---
# This fixes the "class not fully defined" error during OpenAPI generation
RestaurantResponse.model_rebuild()
RestaurantListResponse.model_rebuild()