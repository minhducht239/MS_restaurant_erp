from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime, date

class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: str = Field(..., pattern=r'^[0-9]{10,11}$')
    loyalty_points: int = Field(default=0, ge=0)
    total_spent: float = Field(default=0.0, ge=0)
    last_visit: Optional[date] = None
    visit_count: int = Field(default=1, ge=0)

class CustomerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^[0-9]{10,11}$')
    loyalty_points: Optional[int] = Field(None, ge=0)
    total_spent: Optional[float] = Field(None, ge=0)
    last_visit: Optional[date] = None
    visit_count: Optional[int] = Field(None, ge=0)

class CustomerOut(BaseModel):
    id: str
    name: str
    email: Optional[str] = None
    phone: str
    loyalty_points: int
    total_spent: float
    last_visit: Optional[date] = None
    visit_count: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class CustomerFilter(BaseModel):
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=10, ge=1, le=100)
    search: Optional[str] = None
    loyalty_points_min: Optional[int] = Field(None, ge=0)
    loyalty_points_max: Optional[int] = Field(None, ge=0)
    total_spent_min: Optional[float] = Field(None, ge=0)
    total_spent_max: Optional[float] = Field(None, ge=0)
    created_at_after: Optional[date] = None
    created_at_before: Optional[date] = None
    ordering: Optional[str] = None