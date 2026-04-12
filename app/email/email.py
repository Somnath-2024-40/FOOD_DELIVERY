import logging
import resend

from core.config import settings


resend.api_key = settings.RESEND_API_KEY
FROM_EMAIL = "FoodDelivery <somnathsingpatar123@gmail.com>"

logger = logging.getLogger(__name__)

async def send_welcome_email(email:str, full_name:str)->None:
    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to":email,
            "subject": "Welcome to FoodDelivery",
            "html": f"""
                <h1>Hi {full_name}</h1>
                <p>Welcome to FoodDelivery</p>
            """}
        )
    except Exception as e:
        logger.error(f"Failed welcome massage to {email}: {e}")

async def send_order_conformation_email(
    email:str,
    full_name:str,
    order_number:int,
    total_amount:float,
    estimated_delivery_time:int
)->None:

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to":email,
            "subject": "order conformation",
            "html":f"""
                <h1>Hi {full_name}</h1>
                <p>your order number is {order_number}</p>
                <p>your total amount is {total_amount}</p>
                <p>your estimated delivery time is {estimated_delivery_time}</p>
            """}
        )
        
    except Exception as e:
        logger.error(f"Failed order conformation massage to {email}: {e}")



async def send_payment_success_email(
    email:str,
    full_name:str,
    order_number:int,
    amount:float
)->None:

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to":email,
            "subject":"payment success",
            "html":f"""
                <h1>Hi {full_name}</h1>
                <p>your order number is {order_number}</p>
                <p>your total amount is {amount}</p>
                <p>your payment is sucessed</p>
            """}
        )
        
    except Exception as e:
        logger.error(f"Failed payment success massage to {email}: {e}")


async def send_payment_failed_email(
    email:str,
    full_name:str,
    order_number:int,
    
)->None:

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to":email,
            "subject":"payment failed",
            "html":f"""
                <h1>Hi {full_name}</h1>
                <p>your order number is {order_number}</p>
                <p>your payment is failed</p>
            """}
        )
        
    except Exception as e:
        logger.error(f"Failed payment failed massage to {email}: {e}")

async def order_status_email(
    email:str,
    full_name:str,
    order_number:int,
    status:str
)->None:

    try:
        resend.Emails.send({
            "from": FROM_EMAIL,
            "to":email,
            "subject":"order status",
            "html":f"""
                <h1>Hi {full_name}</h1>
                <p>your order number is {order_number}</p>
                <p>your order status is {status}</p>
            """}
        )
    except Exception as e:
        logger.error(f"Failed order status massage to {email}: {e}")




