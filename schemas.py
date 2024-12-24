from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EventStatus(str, Enum):
    active = "active"
    closed = "closed"
    cancelled = "cancelled"

class TransactionType(str, Enum):
    expense = "expense"
    revenue = "revenue"

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
    status: EventStatus
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

class TicketAvailability(BaseModel):
    ticket_id: str
    ticket_type: str
    price: float
    available: bool
    total_sold: int

class TicketAvailabilityResponse(BaseModel):
    tickets: List[TicketAvailability]

    class Config:
        orm_mode = True

class TicketSaleHistory(BaseModel):
    sale_id: str
    ticket_type: str
    quantity: int
    total_amount: float
    purchase_date: datetime

class TicketSalesHistoryResponse(BaseModel):
    event_id: str
    total_sales: int
    total_revenue: float
    sales: List[TicketSaleHistory]

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
    type: TransactionType  # 'revenue' or 'expense'
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

class WeeklyFinancialReport(FinancialReport):
    week_start: str  # Format 'YYYY-MM'
    week_end: str

class MeetingBase(BaseModel):
    date: str
    time: str
    location: str
    agenda: str

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

class ItemResponse(BaseModel):
    name: str
    total_quantity: int
    total_revenue: float

class TopItemsResponse(BaseModel):
    items: list[ItemResponse]

class BulkSaleResponse(BaseModel):
    total_revenue: float
    sales_count: int

class AvailableResponse(BaseModel):
    available: bool

class LowStockItemResponse(BaseModel):
    id: str
    name: str
    current_quantity: int
    price: float

class InventoryAlertResponse(BaseModel):
    low_stock_items: List[LowStockItemResponse]

class RevenueSourceResponse(BaseModel):
    description: str
    total_amount: float
    transaction_count: int

class TopRevenueSourcesResponse(BaseModel):
    sources: List[RevenueSourceResponse]

class Period(BaseModel):
    year: int
    month: int

class ProfitReportResponse(BaseModel):
    period: Period
    total_revenue: float
    total_expenses: float
    net_profit: float
    profit_margin: float

class DailyBreakdown(BaseModel):
    date: str  # using str for date formatting
    revenue: float
    expense: float

class DailyRevenueResponse(BaseModel):
    daily_breakdown: List[DailyBreakdown]

class DateRange(BaseModel):
    start: str
    end: str

class EventStatisticsResponse(BaseModel):
    total_events: int
    active_events: int
    closed_events: int
    cancelled_events: int
    total_revenue: float
    date_range: DateRange


class DuplicateEventResponse(BaseModel):
    new_event_id: str
    name: str
    date: str
    time: datetime

class SearchEventsResponse(BaseModel):
    total_results: int
    events: List[str]

class CapacityAnalysisEvent(BaseModel):
    event_id: str
    name: str
    date: str
    tickets_sold: int
    status: EventStatus

class CapacityAnalysisResponse(BaseModel):
    capacity_analysis: List[CapacityAnalysisEvent]

class ObservationResponse(BaseModel):
    id: str
    eventId: str
    content: str
    createdAt: datetime

class ObservationInput(BaseModel):
    content: str

class SaleItem(BaseModel):
    name: str
    quantity: int
    revenue: float

class TicketSaleDetail(BaseModel):
    type: str
    price: float
    quantity_sold: int
    revenue: float

class SalesData(BaseModel):
    total_revenue: float
    tickets_sold: List[TicketSaleDetail]
    items_sold: List[SaleItem]

class EventDetailsResponse(BaseModel):
    id: str
    name: str
    date: str
    time: str
    location: str
    status: EventStatus
    sales: SalesData
    observations: List[ObservationInput]

class DateInput(BaseModel):
    date: str
    time: str

class RescheduleEventResponse(BaseModel):
    id: str
    date: str
    time: str


class ReopenEventResponse(BaseModel):
    id: str
    status: EventStatus

class CancelEventResponse(ReopenEventResponse):
    cancelledAt: datetime

class TicketSales(BaseModel):
    total_revenue: float
    details: List[TicketSaleDetail]

class ItemSaleDetail(BaseModel):
    name: str
    price: float
    quantity_sold: int
    revenue: float
    remaining_stock: int

class ItemSales(BaseModel):
    total_revenue: float
    details: List[ItemSaleDetail]

class EventFinancialReport(BaseModel):
     ticket_revenue: int
     item_revenue: int
     total_revenue: int

class EventReportResponse(BaseModel):
    event_id: str
    event_name: str
    status: EventStatus
    time: str
    date: str
    financial_summary: EventFinancialReport
    ticket_sales: TicketSales
    item_sales: ItemSales

class User(BaseModel):
    username: str
    password: str
    role: Optional[str] = "member"

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordChangeRequest(BaseModel):
    new_password: str