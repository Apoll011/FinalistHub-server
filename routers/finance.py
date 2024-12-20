from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import uuid
import models, schemas
from database import get_db
from datetime import datetime
from sqlalchemy.sql.expression import extract
from typing import Dict, Optional, List

router = APIRouter()

@router.post("/revenue", response_model=schemas.FinancialTransaction)
def add_revenue(
        description: str,
        amount: float,
        db: Session = Depends(get_db)
):
    transaction = models.Transaction(
        id=str(uuid.uuid4()),
        type="revenue",
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
        type="expense",
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
        models.Transaction.type == "revenue"
    ).with_entities(func.sum(models.Transaction.amount)).scalar() or 0

    expenses = db.query(models.Transaction).filter(
        models.Transaction.type == "expense"
    ).with_entities(func.sum(models.Transaction.amount)).scalar() or 0

    return {
        "current_balance": revenue - expenses,
        "last_updated": datetime.utcnow()
    }

@router.get("/transactions", response_model=schemas.FinancialReport)
def get_transactions(db: Session = Depends(get_db)):
    transactions = db.query(models.Transaction) \
        .all()

    total_revenue = sum(t.amount for t in transactions if t.type == "revenue")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")
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

    total_revenue = sum(t.amount for t in transactions if t.type == "revenue")
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")

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
    ).filter(models.Transaction.type == "revenue")

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
def get_daily_revenue(
        start_date: str = datetime.now().strftime("%Y-%m-%d"),
        end_date: str = datetime.now().strftime("%Y-%m-%d"),
        db: Session = Depends(get_db)
):
    """Get daily revenue breakdown"""
    query = db.query(
        func.date(models.Transaction.timestamp).label('date'),
        func.sum(models.Transaction.amount).label('revenue')
    ).filter(
        models.Transaction.type == "revenue",
        models.Transaction.timestamp.between(start_date, end_date)
    ).group_by(func.date(models.Transaction.timestamp)) \
        .order_by(text('date'))

    daily_revenue = query.all()

    return {
        "daily_breakdown": [
            {
                "date": str(day.date),
                "revenue": day.revenue
            } for day in daily_revenue
        ]
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

    revenue = sum(t.amount for t in transactions if t.type == "revenue")
    expenses = sum(t.amount for t in transactions if t.type == "expense")

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