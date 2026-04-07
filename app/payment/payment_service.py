from decimal import Decimal
import logging

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from models.order import Order
from models.Idempotency import IdempotencyKey
from models.user import User
from models.enums import UserRole, OrderStatus
from payment.payment_model import Payment
from payment.payment_enum import PaymentStatus, PaymentMethod
from payment.payment_schema import PaymentCreate, PaymentResponse


logger = logging.getLogger(__name__)


async def _idempotency_key_exists(
    db: AsyncSession,
    key: str,
    order_id: int,
    entity_type: str = "payment"
) -> bool:

    exist = await db.execute(
        select(Payment).where(
            IdempotencyKey.key == key,
            IdempotencyKey.entity_type == entity_type
        )
    )

    if exist.scalar_one_or_none():
        return True #true mean duolicate

    idem = IdempotencyKey(
        key=key,
        order_id=order_id,
        entity_type=entity_type
    )

    db.add(idem)
    await db.commit()

    return False  #this is for fresh key



async def _get_order_with_payment(
    db: AsyncSession,
    order_id: int
) -> Order | None:

    query = select(Order).where(Order.id == order_id).options(selectinload(Order.payment))
    result = await db.execute(query)
    return result.scalar_one_or_none()  


async def create_payment(
    db: AsyncSession,
    payment_in: PaymentCreate,
    current_user: User,
    idem_key: str
) -> PaymentResponse:


    duplicate = await _idempotency_key_exists(db, idem_key, payment_in.order_id)
    if duplicate:
        is_exist = await db.execute(select(Payment).where(Payment.order_id == payment_in.order_id))
        payment = is_exist.scalar_one_or_none()

        if payment:
            return PaymentResponse.model_validate(payment)  #return same payment 

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already done")

    order = await _get_order_with_payment(db, payment_in.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.id != order.customer_id:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if order.status == OrderStatus.DELIVERED: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment only done after delivery")

    if order.payment:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment already done")

    payment = Payment(
        customer_id=payment_in.customer_id,
        order_id=payment_in.order_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        status=PaymentStatus.PAID,
        upi_ref=payment_in.upi_ref,
        notes=payment_in.notes
    )

    try:
        db.add(payment)
        await db.flush()
        order.payment_status = PaymentStatus.PAID
        await db.commit()
        await db.refresh(payment)
    except Exception as e:
        await db.rollback()
        logger.error(e) 
        raise

    return payment


async def get_payment_by_payment_id(
    db: AsyncSession,
    payment_id: int,
    current_user: User
) -> PaymentResponse:

    result = await db.execute(select(Payment).where(Payment.id == payment_id))
    payment = result.scalar_one_or_none() 

    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    if current_user.role == UserRole.CUSTOMER and payment.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    return PaymentResponse.model_validate(payment)  


async def get_payment_by_order(
    db: AsyncSession,
    current_user: User,
    order_id: int
) -> PaymentResponse:

    order = await _get_order_with_payment(db, order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.role == UserRole.CUSTOMER and order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if not order.payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    return PaymentResponse.model_validate(order.payment)  