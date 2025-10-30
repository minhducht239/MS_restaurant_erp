from pydantic import BaseModel, constr, condecimal
from typing import Optional
from datetime import datetime

class MenuItemBase(BaseModel):
    name: constr(min_length=1, max_length=100)
    description: Optional[str] = None
    price: condecimal(gt=0)
    category: constr(regex="^(food|drink)$")
    is_available: bool = True

class MenuItemCreate(MenuItemBase):
    pass

class MenuItemUpdate(MenuItemBase):
    pass

class MenuItemOut(MenuItemBase):
    id: str
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime