from enum import Enum
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    PROCESSING = "processing"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, enum.Enum):
    PAY_ON_DELIVERY = "pay_on_delivery"
    UPI = "upi"
    BANK_TRANSFER = "bank_transfer"




    