

from fastapi import HTTPException, status,Header
from decimal import Decimal, ROUND_HALF_UP
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
import uuid
from typing import Tuple,Optional,List
from sqlalchemy import func,ForeignKey
from sqlalchemy.orm import selectinload

from models.order import OrderItem,Order,PaymentMethod,PaymentStatus,OrderStatus
from models.menu import MenuItem,MenuCategory
from models.restaurant import Restaurant,RestaurantStatus
from models.user import User,UserRole
from schemas.order import OrderCreate, OrderStatusUpdate
from core.dependencies import DB
from models.Idempotency import IdempotencyKey




MAX_PAGE_SIZE = 50

# helper functions
def _generate_order_number(session:AsyncSession) ->str:
    return "ORD-" + uuid.uuid4().hex[:8].upper()

def _to_decimal(value:float | Decimal,places:int=2):
    quantizer = Decimal(10) ** -places  # example ---------->  Decimal('0.01') for 2 places ....yo bebe
    return Decimal(str(value)).quantize(quantizer, rounding=ROUND_HALF_UP)

_VALID_TRANSITIONS : dict[OrderStatus,frozenset[OrderStatus]] = {
    OrderStatus.PENDING : frozenset({OrderStatus.CONFIRMED,OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED : frozenset({OrderStatus.PREPARING,OrderStatus.CANCELLED}),
    OrderStatus.PREPARING : frozenset({OrderStatus.READY_FOR_PICKUP,OrderStatus.OUT_FOR_DELIVERY,OrderStatus.CANCELLED}),
    OrderStatus.READY_FOR_PICKUP : frozenset({OrderStatus.DELIVERED,OrderStatus.CANCELLED}),
    OrderStatus.OUT_FOR_DELIVERY : frozenset({OrderStatus.DELIVERED,OrderStatus.CANCELLED}),
    OrderStatus.DELIVERED : frozenset(),
    OrderStatus.CANCELLED : frozenset()
}
    

def _assert_valid_transition(current_status:OrderStatus,new_status:OrderStatus):
    allowed_status = _VALID_TRANSITIONS[current_status,frzenset()]
    if new not in allowed_status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status transition from {current_status} to {new_status}"
        )

async def get_order(db:AsyncSession, order_id:int)-> Optional[Order]:
    result = await db.execute(select(Order).where(Order.id==order_id).options(selectinload(Order.items)))
    return result.scalar_one_or_none()

async def get_order_or_404(db:AsyncSession,order_id:int)->Order:
    order = await get_order(db,order_id)
    if not order:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND,detail="Order not found")
    return order


# paggination

async def _clamp_page_size(page_size:int)->int:
    return max(1,min(page_size,MAX_PAGE_SIZE))

async def List_order_for_customers(
    db:AsyncSession,
    customer_id:int,
    page:int = 1,
    page_size:int = 10

)->Tuple[List[Order],int]:

    page_size = await _clamp_page_size(page_size)
    base = (
        select(Order).where(Order.customer_id == customer_id).order_by(Order.created_at.desc())
    )

    total = await _count(db,base)
    result = await db.execute(base.offset((page-1)*page_size).limit(page_size))
    return result.scalars().all(),total

async def List_order_for_restaurant(
    db:AsyncSession,
    restaurant_id:int,
    page:int = 1,
    page_size:int = 10,
    order_status:Optional[OrderStatus] = None
)->Tuple[List[Order],int]:

    page_size = await _clamp_page_size(page_size)

    base = (
        select(Order).where(Order.restaurant_id == restaurant_id).order_by(Order.created_at.dec())
    )
    if order_status is not None:
        base = base.where(Order.status == order_status)
    result = await db.execute(base.offset((page-1)*page_size).limit(page_size))
    total = await _count(db,base)
    return result.scalars().all(),total

async def get_all_order(
    db:AsyncSession,
    page:int = 1,
    page_size:int = 10,
    order_status:Optional[OrderStatus] = None
)->Tuple[List[Order],int]:

    page_size = await _clamp_page_size(page_size)
    base=(
        select(Order).order_by(Order.created_at.desc())
    )
    if order_status is not None:
        base = base.where(Order.status == order_status)
    total = await _count(db,base)
    result = await db.execute(base.offset((page-1)*page_size).limit(page_size))
    return result.scalars().all(),total

async def _count(db:AsyncSession,base_query):
    count_query = select(func.count()).select_from(base_query.subquery())
    result = await db.execute(count_query)
    return result.scalar()


# create and update operations

async def _get_order_with_items(db: AsyncSession, order_id: int) -> Order:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )
    return result.scalar_one_or_none()

async def create_order(
    db:AsyncSession,
    order_in:OrderCreate,
    customer:User,
    x_idempotency_key:Optional[str] = None

)->Order:

    if not x_idempotency_key:
        raise HTTPException(
            status_code  = status.HTTP_400_BAD_REQUEST,
            detail = "Idempotency key header is required"
        )

    existing_key = await db.execute(
        select(IdempotencyKey).where(IdempotencyKey.key == x_idempotency_key)

    )

    existing_key_record = existing_key.scalar_one_or_none()

    if existing_key_record:
        order = await _get_order_with_items(db, existing_key_record.order_id)
        if order is None:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = "Inconsistent state: Idempotency key exists without associated order"
            )
        return order


    




    restaurant_result = await db.execute(
        select(Restaurant).where(Restaurant.id == order_in.restaurant_id,Restaurant.status == RestaurantStatus.OPEN,Restaurant.is_active.is_(True))
    )
    restaurant =restaurant_result.scalar_one_or_none()
    if restaurant is None:
        raise HTTPException( 
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "restaurant not found"
        )

    # if restaurant.status != RestaurantStatus.OPEN:
    #     raise HTTPException(
    #         status_code = status.HTTP_400_BAD_REQUEST,
    #         detail = "Restaurant currently not able to take orders"
    #     )

    if not order_in.items:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "Order must contain at least one item"
        )
    

    requested_ids = [item.menu_item_id for item in order_in.items]

    menu_result = await db.execute(
        select(MenuItem).where(
            MenuItem.id.in_(requested_ids),
            MenuItem.is_available.is_(True),
            MenuItem.restaurant_id == restaurant.id
        )
    )
    menu_items = {item.id: item for item in menu_result.scalars().all()}



# ---------build order and made calculations
    subtotal = Decimal(0.0)
    order_items:List[OrderItem] = []

    for item_in in order_in.items:
        menu_item = menu_items.get(item_in.menu_item_id)
        if not menu_item:
            raise HTTPException(
                
                    status_code = status.HTTP_400_BAD_REQUEST,
                    detail = f"Menu item {item_in.menu_item_id} not found"
                
            )
        

        unit_price = _to_decimal(menu_item.price)
        line_total =_to_decimal(unit_price * item_in.quantity)
        subtotal += line_total
        
        order_items.append(
            OrderItem(
                menu_item_id = menu_item.id,
                quantity = item_in.quantity,
                unit_price = unit_price,
                total_price = line_total,
                special_request = item_in.special_request
            )
        )

    
# ---------------------------

    min_order = _to_decimal(restaurant.min_order_price)
    if subtotal <min_order:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = f"order amount must be at least {min_order}"
        )

    delivery_fee = _to_decimal(restaurant.delivery_fee)
    total_amount = _to_decimal(subtotal + delivery_fee)

    order = Order(
        order_number = _generate_order_number(db), 
        subtotal = subtotal,
        delivery_fee = delivery_fee,
        discount = Decimal("0.0"),
        total_amount = total_amount,
        payment_method = order_in.payment_method,
        delivery_address = order_in.delivery_address,
        special_request = order_in.special_request,
        estimated_delivery_time = restaurant.estimated_delivery_time,
        items = order_items,
        customer_id = customer.id,
        restaurant_id = restaurant.id
    )

    try:

        db.add(order)
        await db.flush()
        idempotency_record = IdempotencyKey(
            key=x_idempotency_key,
            order_id=order.id
        )
        db.add(idempotency_record)
        await db.commit()
        order = await _get_order_with_items(db, order.id)
    except Exception:
        await db.rollback()
        raise

    return order


async def update_order_status(
    db:AsyncSession,
    order:Order,
    order_status:OrderStatus,
    requester:User
) ->User:

    if requester.role == UserRole.CUSTOMER:
        if order.customer_id != requester.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only modify your own orders.",
            )
        if new_status != OrderStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Customers may only cancel orders.",
            )

    _assert_valid_transition(order.status, new_status)

    try:
        order.status = new_status
        if order.status == OrderStatus.DELIVERED:
            order.payment_status = PaymentStatus.PAID
        await db.commit()
        await db.refresh(order)

    except Exception:
        await db.rollback()
        raise

    return order


async def assign_delivery_agent(
    db: AsyncSession,
    order: Order,
    agent_id: int,
    requester: User,
) -> Order:
    if requester.role not in (UserRole.ADMIN, UserRole.OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins or owners can assign delivery agents.",
        )

    agent_result = await db.execute(
        select(User).where(
            User.id == agent_id,
            User.role == UserRole.DELIVERY_AGENT,
            User.is_active.is_(True),  
        )
    )
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Active delivery agent not found.",
        )

    try:
        order.delivery_agent_id = agent_id
        await db.commit()
        await db.refresh(order)
    except Exception:
        await db.rollback()
        raise

    return order