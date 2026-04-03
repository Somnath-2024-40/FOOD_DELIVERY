from db.base import Base
from sqlalchemy import Column,String,Integer,Boolean,ForeignKey
from fastapi import HTTPException,Header
from datetime import datetime
from sqlalchemy import DateTime


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), unique=True, nullable=False)
    order_id = Column(Integer,ForeignKey("orders.id"), nullable=True)  
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


