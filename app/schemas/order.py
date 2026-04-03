
from pydantic import BaseModel
from typing import Optional,List
from datetime import datetime


from models.order import PaymentStatus,OrderStatus,PaymentMethod
from schemas.menu import MenuItemResponse

class orderItemCreate(BaseModel):
    menu_item_id:int
    quantity:int
    special_request:Optional[str]=None

class OrderItemResponse(BaseModel):
    id:int
    quantity:int
    unit_price:float
    total_price:float
    special_request:Optional[str]=None

    model_config = {
        "from_attributes":True
    }


class OrderCreate(BaseModel):
    restaurant_id:int
    delivery_address:str
    items:List[orderItemCreate]
    payment_method:PaymentMethod = PaymentMethod.CASH
    special_request:Optional[str]=None

class OrderStatusUpdate(BaseModel):
    status:OrderStatus=OrderStatus.PENDING

class OrderAssignDelivery(BaseModel):
    delivery_agent_id:int   

class OrderResponse(BaseModel):
    id:int
    order_number:str
    status:OrderStatus
    subtotal:float
    delivery_fee:float
    discount:float
    total_amount:float
    payment_status:PaymentStatus
    payment_method:PaymentMethod
    delivery_address:str
    special_request:Optional[str]=None
    estimated_delivery_time:Optional[int]=None
    customer_id:int
    restaurant_id:int
    delivery_agent_id:Optional[int]=None
    items:List[OrderItemResponse]
    created_at:datetime


    model_config = {
        "from_attributes":True
    }


class OrderSummary(BaseModel):
    id:int
    order_number:str
    status:OrderStatus
    total_amount:float
    restaurant_id:int
    created_at:datetime

    model_config = {
        "from_attributes":True
    }