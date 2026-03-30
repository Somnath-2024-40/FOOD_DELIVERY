from enum import Enum
import enum


class RestaurantStatus(str,enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    SUSPENDED = "suspended"


class UserRole(enum.Enum):
    CUSTOMER = "customer"
    DELIVERY_AGENT = "delivery_agent"
    OWNER = "owner"
    ADMIN = "admin


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY_FOR_PICKUP = "ready_for_pickup"
    OUT_FOR_DELIVERY = "out_for_delivery"               
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    ONLINE = "online"
    WALLET = "wallet"

class MenuCategory(str, enum.Enum):
    APPETIZER = "appetizer"
    MAIN_COURSE = "main course"
    DESSERT = "dessert"
    BEVERAGE = "beverage"
    SIDE_DISH = "side dish"
    COMBO = "combo"
    OTHER = "other"


    