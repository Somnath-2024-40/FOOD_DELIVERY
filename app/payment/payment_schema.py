from pydantic import BaseModel
from payment.payment_enum import PaymentMethod, PaymentStatus
from typing import Optional
from models.order import Order
from decimal import Decimal
from datetime import datetime
from pydantic import model_validator


class PaymentCreate(BaseModel):
    order_id: int
    amount:float
    customer_id: int 
    payment_method: PaymentMethod = PaymentMethod.PAY_ON_DELIVERY
    upi_ref: Optional[str]=None
    notes:Optional[str]=None
    # status: PaymentStatus = PaymentStatus.PENDING
    @model_validator(mode='after')
    def upi_ref_required_for_upi(self):
        if self.payment_method == PaymentMethod.UPI and not self.upi_ref:
            raise ValueError("upi_ref is required for UPI payment method")
        return self
    model_config = {
        "from_attributes": True
        }

class PaymentResponse(BaseModel):
    id: int
    customer_id: int
    order_id: int
    amount: Decimal
    payment_method: PaymentMethod
    status: PaymentStatus
    created_at: datetime

    class Config:
        from_attributes = True


class RefundResponse(BaseModel):
    payment_id:int
    order_id:int
    amount:Decimal
    status:PaymentStatus
    massage:str

    class Config:
        from_attributes = True

