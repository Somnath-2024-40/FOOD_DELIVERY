# menu.py
from sqlalchemy import Column, String, Boolean, Integer, Numeric, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
import enum

from db.base import Base, Timestamp
from payment.payment_enum import PaymentStatus, PaymentMethod
from models.order import Order, OrderItem
from models.user import User


class Payment(Base, Timestamp):
    __tablename__ = "payments"

    id = Column(Integer,primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.PAY_ON_DELIVERY, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    upi_ref = Column(String(255), nullable=True)
    notes = Column(Text,nullable=True)

    
    customer = relationship("User", back_populates="payments")
    order = relationship("Order", back_populates="payment")



