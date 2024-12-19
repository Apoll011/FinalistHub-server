from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EventBase(BaseModel):
    name: str
    date: str
    time: str
    location: str
    description: str

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: str
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

class TicketBase(BaseModel):
    type: str
    price: float

class TicketCreate(TicketBase):
    pass

class Ticket(TicketBase):
    id: str
    event_id: str
    available: bool
    created_at: datetime

    class Config:
        orm_mode = True

class ItemBase(BaseModel):
    name: str
    quantity: int
    price: float

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: str
    event_id: Optional[str]
    created_at: datetime

    class Config:
        orm_mode = True

class SaleBase(BaseModel):
    quantity_sold: int

class SaleCreate(SaleBase):
    item_id: str

class Sale(SaleCreate):
    id: str
    total_revenue: float
    timestamp: datetime

    class Config:
        orm_mode = True