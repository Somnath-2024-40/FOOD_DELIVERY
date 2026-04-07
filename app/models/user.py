import enum 
from sqlalchemy import Column,Integer,String,Boolean,ForeignKey
from sqlalchemy.orm import relationship
import enum
from sqlalchemy import Enum

from db.base import Base,Timestamp
from models.enums import UserRole


class User(Base,Timestamp):
    __tablename__ = "users"

    id = Column(Integer,primary_key = True, index = True)
    email = Column(String(255),nullable = False,unique = True)
    hashed_password = Column(String(255),nullable = False)
    full_name = Column(String(255),nullable = False)
    phone_number = Column(String(20), nullable=True)
    role = Column(Enum(UserRole),default=UserRole.CUSTOMER,nullable = False)
    is_active = Column(Boolean, default=True)
    address = Column(String(255),nullable = True)

    # relationships
    restaurants = relationship("Restaurant", back_populates="owner")
    orders = relationship("Order", foreign_keys="[Order.customer_id]", back_populates="customer")
    delivered_orders = relationship("Order", foreign_keys="[Order.delivery_agent_id]", back_populates="delivery_agent")
    payments = relationship("Payment", back_populates="customer")