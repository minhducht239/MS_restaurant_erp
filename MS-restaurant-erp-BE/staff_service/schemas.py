from pydantic import BaseModel, constr, condecimal
from typing import Optional
from datetime import datetime, date

class StaffBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    phone: constr(min_length=8, max_length=15)
    role: constr(pattern="^(manager|cashier|chef|waiter|janitor)$")
    salary: condecimal(gt=0)
    hire_date: date

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    phone: Optional[constr(min_length=8, max_length=15)] = None
    role: Optional[constr(pattern="^(manager|cashier|chef|waiter|janitor)$")] = None
    salary: Optional[condecimal(gt=0)] = None
    hire_date: Optional[date] = None

class StaffOut(StaffBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None