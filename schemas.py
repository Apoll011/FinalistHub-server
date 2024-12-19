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

class PriceQuantity(BaseModel):
    quantity: int
    price: float

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

class ItemCustom(ItemBase):
    id: str
    quantity_sold: int
    total_revenue: float
    timestamp: datetime

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

class ItemSold(BaseModel):
    name: str
    quantity: int
    unit_price: float
    total_price: float

class SalesSummaryResponse(BaseModel):
    event_id: str
    total_sales: float
    items_sold: List[ItemSold]
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

class ItemResponse(BaseModel):
    name: str
    total_quantity: int
    total_revenue: float

class TopItemsResponse(BaseModel):
    items: list[ItemResponse]

class HourlyBreakdownResponse(BaseModel):
    hour: int
    revenue: float
    transactions: int

class SalesResponse(BaseModel):
    date: datetime
    hourly_breakdown: list[HourlyBreakdownResponse]

class BulkSaleResponse(BaseModel):
    total_revenue: float
    sales_count: int


class LowStockItemResponse(BaseModel):
    id: int
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
    new_event_id: int
    name: str
    date: str
    time: datetime

class SearchEventsResponse(BaseModel):
    total_results: int
    events: List[Event]

class TrendingEvent(BaseModel):
    id: int
    name: str
    date: str
    ticket_sales: int

class EventTrendingResponse(BaseModel):
    trending_events: List[TrendingEvent]

class CapacityAnalysisEvent(BaseModel):
    event_id: str
    name: str
    date: str
    tickets_sold: int
    status: str

class CapacityAnalysisResponse(BaseModel):
    capacity_analysis: List[CapacityAnalysisEvent]

class HistoricalData(BaseModel):
    date: str
    count: int

class EventForecastResponse(BaseModel):
    event_id: int
    current_sales: int
    predicted_attendance: int
    historical_data: List[HistoricalData]

class ObservationResponse(BaseModel):
    id: int
    eventId: int
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
    status: str
    sales: SalesData
    observations: List[ObservationInput]

class RescheduleEventResponse(BaseModel):
    id: int
    date: datetime
    time: datetime


class CancelEventResponse(BaseModel):
    id: int
    status: str
    cancelledAt: datetime

class EventRevenueRanking(BaseModel):
    id: int
    name: str
    date: str
    ticket_revenue: float
    item_revenue: float
    total_revenue: float

class RevenueRankingResponse(BaseModel):
    events: List[EventRevenueRanking]

class TicketSales(BaseModel):
    total_revenue: float
    details: List[TicketSaleDetail]

class ItemSaleDetail(BaseModel):
    type: str
    price: float
    quantity_sold: int
    revenue: float

class ItemSales(BaseModel):
    total_revenue: float
    details: List[ItemSaleDetail]

class EventClosingResponse(BaseModel):
    event_id: str
    event_name: str
    status: str
    closed_at: datetime
    financial_summary: dict  # Contains ticket_revenue, item_revenue, total_revenue
    ticket_sales: TicketSales
    item_sales: ItemSales
