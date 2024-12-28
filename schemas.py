from pydantic import BaseModel,Field
from typing import Any, AnyStr, List, Optional, Dict
from datetime import datetime
from enum import Enum

class EventStatus(str, Enum):
    active = "active"
    closed = "closed"
    cancelled = "cancelled"

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

class Balance(BaseModel):
    current_balance: float
    last_updated: datetime

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


class PaymentMethod(str, Enum):
    CASH = "cash"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PIX = "pix"
    OTHER = "other"

class TransactionType(str, Enum):
    REVENUE = "revenue"
    EXPENSE = "expense"
    TRANSFER = "transfer"

class AccountType(str, Enum):
    BANK = "bank"
    CASH = "cash"

class AccountBase(BaseModel):
    name: str
    type: AccountType
    description: Optional[str] = None

class AccountCreate(AccountBase):
    pass

class AccountResponse(AccountBase):
    id: str
    current_balance: float
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class AccountBalanceResponse(BaseModel):
    id: str
    name: str
    type: AccountType
    current_balance: float
    last_updated: datetime

    class Config:
        orm_mode = True

class TransactionBase(BaseModel):
    type: TransactionType
    amount: float = Field(gt=0)
    description: Optional[str] = None
    payment_method: Optional[PaymentMethod] = None
    from_account_id: Optional[str] = None
    to_account_id: Optional[str] = None
    category_id: Optional[str] = None
    event_id: Optional[str] = None
    receipt_number: Optional[str] = None
    notes: Optional[str] = None
    created_by: Optional[str] = None
    created_at: datetime
    updated_at: datetime

class CloseEventRequest(BaseModel):
    event_id: str
    user_id: str
    to_account_id: str

class TransactionCreate(TransactionBase):
    created_by: str

class TransactionResponse(TransactionBase):
    id: str
    receipt_file: Optional[str] = None
    reconciliation_status: Any
    reconciliation_notes: Optional[str] = None

    class Config:
        orm_mode = True

class TransactionReconciliation(BaseModel):
    notes: str

class FinancialTransaction(BaseModel):
    id: str
    type: TransactionType
    description: str
    amount: float
    timestamp: datetime

    class Config:
        orm_mode = True

class FinancialReport(BaseModel):
    total_revenue: float
    total_expenses: float
    net_income: float
    transactions: List[FinancialTransaction]

class MonthlyFinancialReport(BaseModel):
    month: str
    total_revenue: float
    total_expenses: float
    net_income: float
    transactions: List[TransactionResponse]

class WeeklyFinancialReport(BaseModel):
    week_start: str
    week_end: str
    total_revenue: float
    total_expenses: float
    net_income: float
    transactions: List[TransactionResponse]

class RevenueSource(BaseModel):
    category: str
    total_amount: float
    transaction_count: int

class TopRevenueSourcesResponse(BaseModel):
    sources: List[RevenueSource]

class StatementTransaction(BaseModel):
    date: datetime
    description: str
    amount: float
    running_balance: float
    type: TransactionType
    category: Optional[str]
    reference: str

class AccountStatement(BaseModel):
    account_id: str
    account_name: str
    start_date: datetime
    end_date: datetime
    opening_balance: float
    closing_balance: float
    transactions: List[TransactionResponse]

class CategorySpending(BaseModel):
    category: str
    total_amount: float
    average_amount: float
    transaction_count: int
    percentage_of_total: float

class CategorySpendingAnalysis(BaseModel):
    categories: List[CategorySpending]
    total_spending: float

class DailyForecast(BaseModel):
    date: datetime
    projected_revenue: float
    projected_expenses: float
    projected_balance: float

class CashflowForecast(BaseModel):
    starting_balance: float
    forecast_period_days: int
    daily_forecasts: List[DailyForecast]

class PendingReconciliationResponse(BaseModel):
    pending_count: int
    total_unreconciled_amount: float
    transactions: List[TransactionResponse]

class TransferHistoryResponse(BaseModel):
    total_transfers: int
    total_amount_transferred: float
    transfers: List[TransactionResponse]

class DailyRevenue(BaseModel):
    date: str
    revenue: float
    expense: float

# Graph and Analytics Schemas
class TimeSeriesDataPoint(BaseModel):
    timestamp: datetime
    value: float

class TimeSeriesData(BaseModel):
    label: str
    data: List[TimeSeriesDataPoint]

class FinancialMetrics(BaseModel):
    current_month_revenue: float
    current_month_expenses: float
    revenue_growth: float  # percentage
    expense_growth: float  # percentage
    profit_margin: float   # percentage
    cash_on_hand: float
    pending_reconciliations: int
    largest_expense: float
    largest_revenue: float

class TransactionDistribution(BaseModel):
    category: str
    amount: float
    percentage: float

class FinancialDashboard(BaseModel):
    metrics: FinancialMetrics
    revenue_by_category: List[TransactionDistribution]
    expenses_by_category: List[TransactionDistribution]
    recent_transactions: List[TransactionResponse]
    cashflow_trend: List[TimeSeriesDataPoint]

class BatchTransactionCreate(BaseModel):
    transactions: List[TransactionCreate]

class BatchTransactionResponse(BaseModel):
    successful: List[TransactionResponse]
    failed: List[Dict[str, str]]

class TransactionCategoryCreate(BaseModel):
    name: str
    description: Optional[str]

# Response schema for category
class TransactionCategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]

    class Config:
        orm_mode = True

# Schema for usage statistics of a category
class CategoryUsageResponse(BaseModel):
    category_id: str
    category_name: str
    total_transactions: int
    total_amount: float
    average_amount: float
    last_used: Optional[datetime]
    transactions: List[TransactionResponse]
