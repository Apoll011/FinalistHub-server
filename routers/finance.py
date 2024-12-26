from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, text, extract
from typing import Optional, List
import uuid
import models, schemas
from database import get_db
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/accounts", response_model=schemas.AccountResponse)
def create_account(
        account: schemas.AccountCreate,
        db: Session = Depends(get_db)
):
    """Create a new account (bank or cash)"""
    new_account = models.Account(
        id=str(uuid.uuid4()),
        **account.dict()
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account

@router.get("/accounts/{account_id}/balance", response_model=schemas.AccountBalanceResponse)
def get_account_balance(
        account_id: str,
        db: Session = Depends(get_db)
):
    """Get current balance and transaction history for an account"""
    account = db.query(models.Account).filter_by(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "id": account.id,
        "name": account.name,
        "type": account.type,
        "current_balance": account.current_balance,
        "last_updated": account.updated_at
    }

@router.post("/transactions", response_model=schemas.TransactionResponse)
async def create_transaction(
        transaction: schemas.TransactionCreate,
        receipt: Optional[UploadFile] = File(None),
        db: Session = Depends(get_db)
):
    """Create a new transaction with optional receipt upload"""
    db_transaction = db.begin_nested()

    try:
        new_transaction = models.Transaction(
            id=str(uuid.uuid4()),
            **transaction.dict(exclude={'receipt_file'})
        )

        if receipt:
            file_path = f"receipts/{new_transaction.id}_{receipt.filename}"
            new_transaction.receipt_file = file_path

        # Update account balances based on transaction type
        if transaction.type == models.TransactionType.TRANSFER:
            from_account = db.query(models.Account).filter_by(id=transaction.from_account_id).first()
            to_account = db.query(models.Account).filter_by(id=transaction.to_account_id).first()

            if not from_account or not to_account:
                raise HTTPException(status_code=404, detail="Account not found")

            from_account.current_balance -= transaction.amount
            to_account.current_balance += transaction.amount

        elif transaction.type == models.TransactionType.EXPENSE:
            account = db.query(models.Account).filter_by(id=transaction.from_account_id).first()
            if not account:
                raise HTTPException(status_code=404, detail="Account not found")
            account.current_balance -= transaction.amount

        else:  # REVENUE
            account = db.query(models.Account).filter_by(id=transaction.to_account_id).first()
            if not account:
                raise HTTPException(status_code=404, detail="Account not found")
            account.current_balance += transaction.amount

        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)

        return new_transaction

    except Exception as e:
        db_transaction.rollback()
        raise HTTPException(status_code=400, detail=str(e))

# Existing Financial Report Routes
@router.get("/balance", response_model=schemas.Balance)
def get_total_balance(db: Session = Depends(get_db)):
    """Get total balance across all accounts"""
    total_balance = db.query(func.sum(models.Account.current_balance)).scalar() or 0

    return {
        "current_balance": total_balance,
        "last_updated": datetime.utcnow()
    }

@router.get("/transactions/monthly", response_model=schemas.MonthlyFinancialReport)
def get_monthly_transactions(db: Session = Depends(get_db)):
    """Get financial report for the current month"""
    current_month = datetime.utcnow().strftime("%Y-%m")

    transactions = db.query(models.Transaction) \
        .filter(extract('year', models.Transaction.created_at) == datetime.utcnow().year) \
        .filter(extract('month', models.Transaction.created_at) == datetime.utcnow().month) \
        .all()

    total_revenue = sum(t.amount for t in transactions if t.type == models.TransactionType.REVENUE)
    total_expenses = sum(t.amount for t in transactions if t.type == models.TransactionType.EXPENSE)

    return {
        "month": current_month,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": total_revenue - total_expenses,
        "transactions": transactions
    }

@router.get("/transactions/weekly", response_model=schemas.WeeklyFinancialReport)
def get_weekly_transactions(db: Session = Depends(get_db)):
    """Get financial report for the current week"""
    start_of_week = (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())).strftime("%Y-%m-%d")
    end_of_week = (datetime.utcnow() + timedelta(days=6 - datetime.utcnow().weekday())).strftime("%Y-%m-%d")

    transactions = db.query(models.Transaction) \
        .filter(models.Transaction.created_at >= start_of_week) \
        .filter(models.Transaction.created_at <= end_of_week) \
        .all()

    total_revenue = sum(t.amount for t in transactions if t.type == models.TransactionType.REVENUE)
    total_expenses = sum(t.amount for t in transactions if t.type == models.TransactionType.EXPENSE)

    return {
        "week_start": start_of_week,
        "week_end": end_of_week,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "net_income": total_revenue - total_expenses,
        "transactions": transactions
    }

@router.get("/top-revenue-sources", response_model=schemas.TopRevenueSourcesResponse)
def get_top_revenue_sources(
        limit: int = 10,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get top revenue sources grouped by category"""
    query = db.query(
        models.TransactionCategory.name,
        func.sum(models.Transaction.amount).label('total_amount'),
        func.count(models.Transaction.id).label('transaction_count')
    ).join(models.Transaction) \
        .filter(models.Transaction.type == models.TransactionType.REVENUE)

    if start_date:
        query = query.filter(models.Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(models.Transaction.created_at <= end_date)

    results = query.group_by(models.TransactionCategory.name) \
        .order_by(text('total_amount DESC')) \
        .limit(limit) \
        .all()

    return {
        "sources": [
            {
                "category": r.name,
                "total_amount": r.total_amount,
                "transaction_count": r.transaction_count
            } for r in results
        ]
    }

@router.get("/accounts/{account_id}/statement", response_model=schemas.AccountStatement)
def get_account_statement(
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        db: Session = Depends(get_db)
):
    """Generate account statement for a specific period"""
    account = db.query(models.Account).filter_by(id=account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    transactions = db.query(models.Transaction).filter(
        ((models.Transaction.from_account_id == account_id) |
         (models.Transaction.to_account_id == account_id)) &
        (models.Transaction.created_at.between(start_date, end_date))
    ).order_by(models.Transaction.created_at).all()

    return {
        "account_id": account_id,
        "account_name": account.name,
        "start_date": start_date,
        "end_date": end_date,
        "opening_balance": account.current_balance - sum(
            t.amount if t.to_account_id == account_id else -t.amount
            for t in transactions
        ),
        "closing_balance": account.current_balance,
        "transactions": transactions
    }

@router.get("/categories/spending-analysis", response_model=schemas.CategorySpendingAnalysis)
def analyze_category_spending(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
):
    """Analyze spending patterns by category"""
    query = db.query(
        models.TransactionCategory.name,
        func.sum(models.Transaction.amount).label('total_amount'),
        func.avg(models.Transaction.amount).label('average_amount'),
        func.count(models.Transaction.id).label('transaction_count')
    ).join(models.Transaction) \
        .filter(models.Transaction.type == models.TransactionType.EXPENSE)

    if start_date:
        query = query.filter(models.Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(models.Transaction.created_at <= end_date)

    results = query.group_by(models.TransactionCategory.name).all()

    total_spending = sum(r.total_amount for r in results)

    return {
        "categories": [
            {
                "category": r.name,
                "total_amount": r.total_amount,
                "average_amount": r.average_amount,
                "transaction_count": r.transaction_count,
                "percentage_of_total": (r.total_amount / total_spending * 100) if total_spending > 0 else 0
            } for r in results
        ],
        "total_spending": total_spending
    }

@router.get("/cashflow/forecast", response_model=schemas.CashflowForecast)
def forecast_cashflow(
        days: int = 30,
        db: Session = Depends(get_db)
):
    """Generate cashflow forecast based on historical patterns"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=30)

    daily_averages = db.query(
        models.Transaction.type,
        func.avg(models.Transaction.amount).label('avg_amount')
    ).filter(
        models.Transaction.created_at.between(start_date, end_date)
    ).group_by(models.Transaction.type).all()

    avg_revenue = next((avg.avg_amount for avg in daily_averages if avg.type == models.TransactionType.REVENUE), 0)
    avg_expenses = next((avg.avg_amount for avg in daily_averages if avg.type == models.TransactionType.EXPENSE), 0)

    current_balance = db.query(func.sum(models.Account.current_balance)).scalar() or 0

    forecast_days = []
    running_balance = current_balance

    for day in range(days):
        forecast_date = end_date + timedelta(days=day + 1)
        running_balance += (avg_revenue - avg_expenses)

        forecast_days.append(
            {
                "date": forecast_date,
                "projected_revenue": avg_revenue,
                "projected_expenses": avg_expenses,
                "projected_balance": running_balance
            }
        )

    return {
        "starting_balance": current_balance,
        "forecast_period_days": days,
        "daily_forecasts": forecast_days
    }

@router.get("/reconciliation/pending", response_model=schemas.PendingReconciliationResponse)
def get_pending_reconciliations(db: Session = Depends(get_db)):
    """Get list of transactions pending reconciliation"""
    pending_transactions = db.query(models.Transaction) \
        .filter(models.Transaction.reconciliation_status == False) \
        .order_by(models.Transaction.created_at.desc()) \
        .all()

    return {
        "pending_count": len(pending_transactions),
        "total_unreconciled_amount": sum(t.amount for t in pending_transactions),
        "transactions": pending_transactions
    }

@router.get("/accounts/transfer-history", response_model=schemas.TransferHistoryResponse)
def get_transfer_history(
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
):
    """Get history of transfers between accounts"""
    query = db.query(models.Transaction) \
        .filter(models.Transaction.type == models.TransactionType.TRANSFER)

    if start_date:
        query = query.filter(models.Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(models.Transaction.created_at <= end_date)

    transfers = query.order_by(models.Transaction.created_at.desc()).all()

    return {
        "total_transfers": len(transfers),
        "total_amount_transferred": sum(t.amount for t in transfers),
        "transfers": transfers
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
            extract('year', models.Transaction.created_at) == year,
            extract('month', models.Transaction.created_at) == month
        )
    else:
        query = query.filter(
            extract('year', models.Transaction.created_at) == year
        )

    transactions = query.all()

    revenue = sum(t.amount for t in transactions if t.type == schemas.TransactionType.REVENUE)
    expenses = sum(t.amount for t in transactions if t.type == schemas.TransactionType.EXPENSE)

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