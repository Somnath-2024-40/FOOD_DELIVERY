# order.py
from sqlalchemy import Column, String, Boolean, Integer, Numeric, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum

from db.base import Base, Timestamp


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"               
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    ONLINE = "online"
    WALLET = "wallet"


class Order(Base, Timestamp):
    __tablename__ = "orders"                            

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(30), unique=True, nullable=False, index=True)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)

    subtotal = Column(Numeric(10, 2), nullable=False)   
    delivery_fee = Column(Numeric(10, 2), default=0.0)
    discount = Column(Numeric(10, 2), default=0.0)
    total_amount = Column(Numeric(10, 2), nullable=False)

    payment_status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)

    delivery_address = Column(Text, nullable=False)
    special_instructions = Column(Text, nullable=True) 
    estimated_delivery_time = Column(Integer, nullable=True)

    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    delivery_agent_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    customer = relationship("User", back_populates="orders", foreign_keys=[customer_id])
    restaurant = relationship("Restaurant", back_populates="orders")
    delivery_agent = relationship("User", back_populates="delivered_orders", foreign_keys=[delivery_agent_id])
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base, Timestamp):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)  
    total_price = Column(Numeric(10, 2), nullable=False)
    special_request = Column(Text, nullable=True)        

    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)       
    menu_item_id = Column(Integer, ForeignKey("menu_items.id"), nullable=False)  

    order = relationship("Order", back_populates="items")
    menu_item = relationship("MenuItem", back_populates="order_items")