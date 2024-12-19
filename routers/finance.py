from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.post("/revenue")
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

@router.get("/balance")
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