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


MAX_RETRY_ATTEMPTS = 3
BASE_RETRY_DELAY = 5

# we will rreplace this with a real payment gateway
async def _fake_payment_gateway(payment_method: PaymentMethod, amount: Decimal) -> None:
    return True


async def _payemnt_retry(payment:Payment, amount: Decimal) -> None:
    payment.status = PaymentStatus.PROCESSING
    await db.commit()

    last_error = None

    for atempt in range(1,MAX_RETRY_ATTEMPTS):
        try:
            logger.info(f"Attempt {atempt} to process payment {payment.id}")

            success = await _fake_payment_gateway(payment.payment_method, amount)

            if success:
                payment.status = PaymentStatus.SUCCESS

                await db.commit()
                logger.info(f"Payment {payment.id} processed successfully")
                return True
        except Exception as e:
            last_error = e
            logger.warning(f"Failed to process payment {payment.id}: {e}")

            if attempt < MAX_RETRY_ATTEMPTS:
                backoff = BASE_RETRY_DELAY * (2 ** (attempt - 1)) 
                logger.info(f"backing off for {backoff} seconds")
                await asyncio.sleep(backoff)

    payment.status = PaymentStatus.FAILED
    await db.commit()

    raise last_error
    return False





    



async def _idempotency_key_exists(
    db: AsyncSession,
    key: str,
    order_id: int,
    entity_type: str = "payment"
) -> bool:

    exist = await db.execute(
        select(IdempotencyKey).where(
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

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Duplicate request but no payment found")

    order = await _get_order_with_payment(db, payment_in.order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    if current_user.id != order.customer_id:  
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    if order.status == OrderStatus.DELIVERED: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Payment only done after delivery")

    if order.payment:
        p = order.payment
        if p.status in (PaymentStatus.PENDING, PaymentStatus.PAID, PaymentStatus.PROCESSING):
            return PaymentResponse.model_validate(p) # if FAILED  then create new attempt

    payment = Payment(
        customer_id=payment_in.customer_id,
        order_id=payment_in.order_id,
        amount=payment_in.amount,
        payment_method=payment_in.payment_method,
        status=PaymentStatus.PENDING,
        upi_ref=payment_in.upi_ref,
        notes=payment_in.notes
    )

    try:
        db.add(payment)
        await db.flush()
        await db.commit()
        await db.refresh(payment)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save payment {payment.id}: {e}")  
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to save payment")
    
    success = await _payemnt_retry(payment, payment_in.amount)

    if not success:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to process payment")

    order.payment_status = PaymentStatus.PAID
    await db.commit()
    await db.refresh(payment)

    return PaymentResponse.model_validate(payment)


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