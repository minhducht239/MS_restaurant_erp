from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    MOMO = "momo"
    BANK_TRANSFER = "bank_transfer"

class BillStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"

class BillItemCreate(BaseModel):
    item_id: str
    item_name: str
    quantity: int
    price: float
    subtotal: float

class BillCreate(BaseModel):
    customer: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    items: List[BillItemCreate]
    total_amount: float
    payment_method: PaymentMethod = PaymentMethod.CASH
    status: BillStatus = BillStatus.PENDING
    note: Optional[str] = None

class BillOut(BaseModel):
    id: str
    customer: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    items: List[dict]
    total_amount: float
    payment_method: str
    status: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class BillUpdate(BaseModel):
    customer: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    status: Optional[BillStatus] = None
    note: Optional[str] = None