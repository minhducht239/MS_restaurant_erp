from pydantic import BaseModel, constr, condecimal
from typing import Optional
from datetime import datetime

class MenuItemBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    price: condecimal(gt=0)
    category: constr(pattern="^(food|drink)$")
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[str] = None
    price: Optional[condecimal(gt=0)] = None
    category: Optional[constr(pattern="^(food|drink)$")] = None
    is_available: Optional[bool] = None

class MenuItemOut(MenuItemBase):
    id: str
    image: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None