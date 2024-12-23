from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import uuid
import models, schemas
from database import get_db
from datetime import datetime, timedelta
from sqlalchemy.sql.expression import extract
from typing import Optional

router = APIRouter()

@router.post("/revenue", response_model=schemas.FinancialTransaction)
def add_revenue(
        description: str,
        amount: float,
        db: Session = Depends(get_db)
):
    transaction = models.Transaction(
        id=str(uuid.uuid4()),
        type=schemas.TransactionType.revenue,
        description=description,
        amount=amount
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.post("/expenses", response_model=schemas.FinancialTransaction)
def add_expenses(
        description: str,
        amount: float,
        db: Session = Depends(get_db)
):
    transaction = models.Transaction(
        id=str(uuid.uuid4()),
        type=schemas.TransactionType.expense,
        description=description,
        amount=amount
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.get("/balance", response_model=schemas.Balance)
def get_balance(db: Session = Depends(get_db)):
    revenue = db.query(models.Transaction).filter(
        models.Transaction.type == schemas.TransactionType.revenue
    ).with_entities(func.sum(models.Transaction.amount)).scalar() or 0

    expenses = db.query(models.Transaction).filter(
        models.Transaction.type == schemas.TransactionType.expense
    ).with_entities(func.sum(models.Transaction.amount)).scalar() or 0

    return {
        "current_balance": revenue - expenses,
        "last_updated": datetime.utcnow()
    }

@router.get("/transactions", response_model=schemas.FinancialReport)
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction) \
        .all()

    total_revenue = sum(t.amount for t in transactions if t.type == schemas.TransactionType.revenue)
    total_expenses = sum(t.amount for t in transactions if t.type == schemas.TransactionType.expense)

    return {
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": total_revenue - total_expenses,
        "transactions": [
            {
                "id": t.id,
                "type": t.type,
                "description": t.description,
                "amount": t.amount,
                "timestamp": t.timestamp
            } for t in transactions
        ]
    }

@router.get("/transactions/monthly", response_model=schemas.MonthlyFinancialReport)
def get_monthly_transactions(db: Session = Depends(get_db)):
    current_month = datetime.utcnow().strftime("%Y-%m")

    # Get all transactions for current month
    transactions = db.query(models.Transaction) \
        .filter(extract('year', models.Transaction.timestamp) == datetime.utcnow().year) \
        .filter(extract('month', models.Transaction.timestamp) == datetime.utcnow().month) \
        .all()

    total_revenue = sum(t.amount for t in transactions if t.type == schemas.TransactionType.revenue)
    total_expenses = sum(t.amount for t in transactions if t.type == schemas.TransactionType.expense)

    return {
        "month": current_month,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": total_revenue - total_expenses,
        "transactions": [
            {
                "id": t.id,
                "type": t.type,
                "description": t.description,
                "amount": t.amount,
                "timestamp": t.timestamp
            } for t in transactions
        ]
    }

@router.get("/transactions/weekly", response_model=schemas.WeeklyFinancialReport)
def get_weekly_transactions(db: Session = Depends(get_db)):
    # Calculate the start and end of the current week
    start_of_week = (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())).strftime("%Y-%m-%d")
    end_of_week = (datetime.utcnow() + timedelta(days=6 - datetime.utcnow().weekday())).strftime("%Y-%m-%d")

    # Get all transactions for the current week
    transactions = db.query(models.Transaction) \
        .filter(models.Transaction.timestamp >= start_of_week) \
        .filter(models.Transaction.timestamp <= end_of_week) \
        .all()

    total_revenue = sum(t.amount for t in transactions if t.type == schemas.TransactionType.revenue)
    total_expenses = sum(t.amount for t in transactions if t.type == schemas.TransactionType.expense)

    return {
        "week_start": start_of_week,
        "week_end": end_of_week,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": total_revenue - total_expenses,
        "transactions": [
            {
                "id": t.id,
                "type": t.type,
                "description": t.description,
                "amount": t.amount,
                "timestamp": t.timestamp
            } for t in transactions
        ]
    }


@router.get("/top-revenue-sources", response_model=schemas.TopRevenueSourcesResponse)
def get_top_revenue_sources(
        limit: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get top revenue sources grouped by description"""
    query = db.query(
        models.Transaction.description,
        func.sum(models.Transaction.amount).label('total_amount'),
        func.count(models.Transaction.id).label('transaction_count')
    ).filter(models.Transaction.type == schemas.TransactionType.revenue)

    if start_date:
        query = query.filter(models.Transaction.timestamp >= start_date)
    if end_date:
        query = query.filter(models.Transaction.timestamp <= end_date)

    results = query.group_by(models.Transaction.description) \
        .order_by(text('total_amount DESC')) \
        .limit(limit) \
        .all()

    return {
        "sources": [
            {
                "description": r.description,
                "total_amount": r.total_amount,
                "transaction_count": r.transaction_count
            } for r in results
        ]
    }

@router.get("/daily-revenue", response_model=schemas.DailyRevenueResponse)
def get_daily_transactions(
    start_date: str = None,  # Allow start_date to be optional
    end_date: str = None,    # Allow end_date to be optional
    db: Session = Depends(get_db)
):
    """Get daily transaction breakdown"""
    # Determine the start_date: last Sunday or today if it's Sunday
    if start_date is None:
        if datetime.now().weekday() == 6:  # Today is Sunday
            start_date = datetime.now().strftime("%Y-%m-%d")
        else:
            start_date = (datetime.now() - timedelta(days=datetime.now().weekday() + 1)).strftime("%Y-%m-%d")  # Last Sunday

    # Calculate the end_date: next Saturday
    if end_date is None:
        end_date = (datetime.now() + timedelta(days=(datetime.now().weekday()))).strftime("%Y-%m-%d")  # Next Saturday

    revenue_query = db.query(
        func.date(models.Transaction.timestamp).label('date'),
        func.sum(models.Transaction.amount).label('revenue')
    ).filter(
        models.Transaction.type == schemas.TransactionType.revenue,
        models.Transaction.timestamp.between(start_date, end_date)
    ).group_by(func.date(models.Transaction.timestamp)) \
        .order_by(text('date'))

    expense_query = db.query(
        func.date(models.Transaction.timestamp).label('date'),
        func.sum(models.Transaction.amount).label('expense')
    ).filter(
        models.Transaction.type == schemas.TransactionType.expense,
        models.Transaction.timestamp.between(start_date, end_date)
    ).group_by(func.date(models.Transaction.timestamp)) \
        .order_by(text('date'))

    revenue_data = {day.date: day.revenue for day in revenue_query.all()}
    expense_data = {day.date: day.expense for day in expense_query.all()}

    # Combine revenue and expense by date
    all_dates = set(revenue_data.keys()).union(expense_data.keys())
    daily_breakdown = [
        {
            "date": str(date),
            "revenue": revenue_data.get(date, 0),
            "expense": expense_data.get(date, 0)
        } for date in sorted(all_dates)
    ]

    return {
        "daily_breakdown": daily_breakdown
    }



@router.get("/profit", response_model=schemas.ProfitReportResponse)
def get_profit_report(
        year: int = datetime.now().year,
        month: Optional[int] = datetime.now().month,
        db: Session = Depends(get_db)
):
    """Generate profit and loss report"""
    query = db.query(models.Transaction)

    if month:
        query = query.filter(
            extract('year', models.Transaction.timestamp) == year,
            extract('month', models.Transaction.timestamp) == month
        )
    else:
        query = query.filter(
            extract('year', models.Transaction.timestamp) == year
        )

    transactions = query.all()

    revenue = sum(t.amount for t in transactions if t.type == schemas.TransactionType.revenue)
    expenses = sum(t.amount for t in transactions if t.type == schemas.TransactionType.expense)

    return {
        "period": {
            "year": year,
            "month": month
        },
        "total_revenue": revenue,
        "total_expenses": expenses,
        "net_profit": revenue - expenses,
        "profit_margin": round((revenue - expenses) / revenue * 100, 2) if revenue > 0 else 0
    }