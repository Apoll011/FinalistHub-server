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

class TicketSaleBase(BaseModel):
    ticket_id: str
    quantity: int

class TicketSaleCreate(TicketSaleBase):
    pass

class TicketSale(TicketSaleBase):
    id: str
    total_amount: float
    created_at: datetime
    ticket_type: str
    event_name: str

    class Config:
        orm_mode = True

class FinancialTransactionBase(BaseModel):
    description: str
    amount: float

class FinancialTransaction(FinancialTransactionBase):
    id: str
    type: str  # 'revenue' or 'expense'
    timestamp: datetime

    class Config:
        orm_mode = True

class Balance(BaseModel):
    current_balance: float
    last_updated: datetime

class FinancialReport(BaseModel):
    total_revenue: float
    total_expenses: float
    net_income: float
    transactions: List[FinancialTransaction]

class MonthlyFinancialReport(FinancialReport):
    month: str  # Format 'YYYY-MM'

class MeetingBase(BaseModel):
    date: str
    time: str
    location: str
    agenda: str

class MeetingCreate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: str

    class Config:
        orm_mode = True

class MeetingList(BaseModel):
    meetings: List[Meeting]

class MeetingMinutes(BaseModel):
    id: str
    meeting_id: str
    file_name: str
    file_size: int
    uploaded_at: datetime