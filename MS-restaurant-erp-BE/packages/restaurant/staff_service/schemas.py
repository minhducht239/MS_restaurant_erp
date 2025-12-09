from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class StaffBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    phone: str = Field(..., min_length=8, max_length=15)
    role: str = Field(..., pattern="^(manager|cashier|chef|waiter|janitor)$")
    salary: Decimal = Field(..., gt=0)
    hire_date: date

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=8, max_length=15)
    role: Optional[str] = Field(None, pattern="^(manager|cashier|chef|waiter|janitor)$")
    salary: Optional[Decimal] = Field(None, gt=0)
    hire_date: Optional[date] = None

class StaffOut(StaffBase):
    id: str
    role_display: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            Decimal: str,
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }

class StaffFilter(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(10, ge=1, le=100)
    role: Optional[str] = None
    search: Optional[str] = None
    ordering: Optional[str] = None
    hire_date: Optional[date] = None