from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
import models, schemas
from database import get_db
from datetime import datetime
from sqlalchemy.sql.expression import extract

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
        type="expenses",
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
        "totalRevenue": total_revenue,
        "totalExpenses": total_expenses,
        "netIncome": total_revenue - total_expenses,
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
        "totalRevenue": total_revenue,
        "totalExpenses": total_expenses,
        "netIncome": total_revenue - total_expenses,
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