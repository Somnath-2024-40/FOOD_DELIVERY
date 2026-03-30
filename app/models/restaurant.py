from sqlalchemy import Column,String,Boolean,Integer,Float,ForeignKey,Text,Enum
import enum
from sqlalchemy.orm import relationship
from db.base import Timestamp

from db.base import Base

class RestaurantStatus(str,enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    SUSPENDED = "suspended"

class Restaurant(Base, Timestamp):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    address = Column(Text, nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(255), nullable=True)
    image_url = Column(String(500), nullable=True)
    cuisine_type = Column(String(100), nullable=True)
    rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    min_order_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    estimated_delivery_time = Column(Integer, default=30)  # minutes
    status = Column(Enum(RestaurantStatus), default=RestaurantStatus.OPEN)
    is_active = Column(Boolean, default=True)

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    
    owner = relationship("User", back_populates="restaurants")
    menu_items = relationship("MenuItem", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="restaurant")
