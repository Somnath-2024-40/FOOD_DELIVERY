from fastapi import HTTPException, status
import asyncio
import logging
from decimal import Decimal
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from background.email import send_welcome_email,send_order_conformation_email,send_payment_success_email,send_payment_failed_email,order_status_email

from db.session import sessionlocal
from models.menu import MenuItem
from models.order import Order
from models.enums import OrderStatus
from payment.payment_enum import PaymentStatus, PaymentMethod
from payment.payment_model import Payment

logger = logging.getLogger(__name__)


#this is fake .. i will replace this with a real payment gateway
async def _fake_payment_gateway(
    method:PaymentMethod,amount:Decimal
)->bool:
    # this is for simulating network latency
    await asyncio.sleep(1)
    return True


# helpers---------------------------------


#this function is for restore the items after cancelation
async def _restore_stock(
    db:AsyncSession,
    order:Order
)->None:

    for item in order.items:
        menu_item = await db.get(MenuItem,item.menu_item_id)
        if menu_item:
            menu_item.quantity += item.quantity
    await db.commit()
    logger.info(f"Restored stock for order {order.id}")

async def _cancel_order(
    db:AsyncSession,
    order:Order,
    customer_email:str,
    customer_name:str
)->None:

    order.status = OrderStatus.CANCELLED
    order.payment_status = PaymentStatus.FAILED
    await db.commit()

    await _restore_stock(db,order)

    await end_payment_failed_email(
        email=customer_email,
        full_name=customer_name,
        order_number=order.id
    )

    logger.info(f"Cancelled order {order.id}")

# ------------------------------------

async def welcome_email(
    email:str,
    full_name:str
)->None:

# this will called from post auth/register.. because common secnse buddy 

    try:
        await send_welcome_email(email,full_name)
    except Exception as e:
        logger.error(f"Failed welcome massage to {email}: {e}")



async def order_conformation_email(
    email:str,
    full_name:str,
    order_number:int,
    total_amount:float,
    estimated_delivery_time:int
)->None:

    try:
        await send_order_conformation_email(
            email=email,
            full_name=full_name,
            order_number=order_number,
            total_amount=total_amount,
            estimated_delivery_time=estimated_delivery_time
        )

    except Exception as e:
        logger.error(f"Failed order conformation massage to {email}: {e}")



async def task_order_status_email(
    email:str,
    full_name:str,
    order_number:int,
    status:str
)->None:

    try:
        await order_status_email(
            email=email,
            full_name=full_name,
            order_number=order_number,
            status=status
        )

    except Exception as e:
        logger.error(f"Failed order status massage to {email}: {e}")

async def send_order_status_update(
    user_email:str,
    full_name:str,
    order_number:int,
    status:str
)->None:

    try:
        await order_status_email(
            email=user_email,
            full_name=full_name,
            order_number=order_number,
            status=status
        )
    except Exception as e:
        logger.error(f"Failed order status massage to {user_email}: {e}")


async def verify_and_finalize_payment(
    order_id:int,
    payment_id:int,
    amount:float,
    payment_method:PaymentMethod
)->None:

    # this will called from post /payments/
    """ 
        1. Load payment + order + customer from DB (own session)
        2. Try gateway — retry up to 3 times with exponential backoff
        3a. Success → mark PAID, confirm order, send success email
        3b. All retries fail → cancel order, restore stock, send failure email
    """

    async with sessionlocal() as db:
        try:

            # --------load payment-------------


            result = await db.execute(
                select(Payment).where(Payment.id == payment_id)
            )

            payment = result.scalar_one_or_none()

            if not payment:
                logger.error(f"Payment {payment_id} not found")
                return

            # --------load order with items + customer---------

            order_result = await db.execute(
                select(Order).where(Order.id == order_id).options(selectinload(Order.items),selectinload(Order.customer))
            )

            order = order_result.scalar_one_or_none()

            if not order:
                logger.error(f"order {order_id} not found")
                return

            customer_email = order.customer.email
            customer_name = order.customer.full_name

            # --------mark as processing_------- 

            payment.status = PaymentStatus.PROCESSING

            await db.commit()

            # ---------try gateway--------------

            success = False
            last_error = None

            for attempt in range(1, MAX_RETRY_ATTEMPTS+1):
                try:
                    logger.info(
                        f"Attempt {attempt} to process payment {payment.id}"
                    )

                    success = await _fake_payment_gateway(payment_method, Decimal(str(amount)))

                    if success:
                        break

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f"Failed to process payment {payment.id}: {e}"
                    )

                if attempt < MAX_RETRY_ATTEMPTS:
                    backoff = BASE_RETRY_DELAY * (2 ** (attempt - 1))
                    logger.info(f"Backing off for {backoff} seconds")
                    await asyncio.sleep(backoff)

            # ---------payment success--------------

            if success:
                payment.status = PaymentStatus.PAID
                order.status = OrderStatus.PAID
                order.payment_status = PaymentStatus.PAID
                await db.commit()

                await order_conformation_email(
                    email=customer_email,
                    full_name=customer_name,
                    order_number=order.id,
                    total_amount=order.total_amount,
                    estimated_delivery_time=order.estimated_delivery_time
                )

            else:
                logger.error(
                    f"Failed to process payment {payment.id}: {last_error}"
                )
                await _cancel_order(db,order,customer_email,customer_name)
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to process payment {payment.id}: {e}")




async def task_cleanup_stuck_orders() -> None:
    """
    Called every 10 minutes by APScheduler (registered in main.py).
 
    Finds orders that are still PENDING after 15 minutes — meaning the
    background payment task crashed before finishing — and cancels them,
    restores stock, and notifies the customer.
 
    This is the safety net that handles cases where task_verify_and_finalize_payment
    itself crashes before completing.
    """
    async with sessionlocal() as db:
        try:
            cutoff = datetime.utcnow() - timedelta(minutes=15)
 
            stuck_result = await db.execute(
                select(Order)
                .where(
                    Order.payment_status == PaymentStatus.PENDING,
                    Order.created_at < cutoff,
                    Order.status != OrderStatus.CANCELLED,
                )
                .options(
                    selectinload(Order.items),
                    selectinload(Order.customer),
                )
            )
            stuck_orders = stuck_result.scalars().all()
 
            if not stuck_orders:
                logger.info("[CLEANUP] No stuck orders found")
                return
 
            logger.warning(f"[CLEANUP] Found {len(stuck_orders)} stuck orders — cancelling")
 
            for order in stuck_orders:
                await _cancel_order(
                    db,
                    order,
                    order.customer.email,
                    order.customer.full_name,
                )
 
        except Exception as e:
            await db.rollback()
            logger.error(f"[CLEANUP] task_cleanup_stuck_orders crashed: {e}")
 
