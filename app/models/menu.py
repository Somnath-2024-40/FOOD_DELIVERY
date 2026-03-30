# menu.py
from sqlalchemy import Column, String, Boolean, Integer, Numeric, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum

from db.base import Base, Timestamp





class MenuItem(Base, Timestamp):                        
    __tablename__ = "menu_items"                        

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)      
    image_url = Column(String(500), nullable=True)
    category = Column(Enum(MenuCategory), default=MenuCategory.OTHER, nullable=False)
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)           
    calories = Column(Integer, nullable=True)
    preparation_time = Column(Integer, nullable=True, default=15)
    is_available = Column(Boolean, default=True)       

    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)

    restaurant = relationship("Restaurant", back_populates="menu_items")
    order_items = relationship("OrderItem", back_populates="menu_item")