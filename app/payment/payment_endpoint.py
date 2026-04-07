from fastapi import HTTPException, status, APIRouter, Depends, Form,Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from core.dependencies import DB
import payment.payment_service as payment_service         
from payment.payment_service import create_payment
from payment.payment_schema import PaymentCreate, PaymentResponse
from payment.payment_enum import PaymentMethod
from core.dependencies import get_current_active_user
from models.user import User


router = APIRouter()


@router.post("/payments/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    db: DB,
    order_id: int = Form(...),
    amount: float = Form(...),
    payment_method: PaymentMethod = Form(default=PaymentMethod.PAY_ON_DELIVERY),
    upi_ref: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user), 
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key") 
) -> PaymentResponse:

    key = idempotency_key or f"payment-{order_id}-customer-{current_user.id}"

    payment_info = PaymentCreate(
        order_id=order_id,
        amount=amount,
        payment_method=payment_method,
        upi_ref=upi_ref,
        notes=notes,
        customer_id=current_user.id, 
    )

    return await create_payment(db, payment_info, current_user,key)  


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment_by_payment_id(                       
    db: DB,
    payment_id: int,
    current_user: User = Depends(get_current_active_user)
) -> PaymentResponse:
    return await payment_service.get_payment_by_payment_id(db, payment_id, current_user)


@router.get("/orders/{order_id}/payment", response_model=PaymentResponse)  # ✅ distinct path
async def get_payment_by_order_id(                         
    db: DB,
    order_id: int,
    current_user: User = Depends(get_current_active_user)
) -> PaymentResponse:
    return await payment_service.get_payment_by_order(db, current_user, order_id)