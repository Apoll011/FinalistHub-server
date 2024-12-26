from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import uuid
import models
import schemas
from database import get_db
from datetime import datetime

router = APIRouter(prefix="/categories", tags=["categories"])

@router.post("/", response_model=schemas.TransactionCategoryResponse)
def create_category(
        category: schemas.TransactionCategoryCreate,
        db: Session = Depends(get_db)
):
    """Create a new transaction category"""
    # Check if category with same name already exists
    existing_category = db.query(models.TransactionCategory).filter(
        func.lower(models.TransactionCategory.name) == func.lower(category.name)
    ).first()

    if existing_category:
        raise HTTPException(
            status_code=400,
            detail="A category with this name already exists"
        )

    new_category = models.TransactionCategory(
        id=str(uuid.uuid4()),
        name=category.name,
        description=category.description
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@router.get("/", response_model=List[schemas.TransactionCategoryResponse])
def list_categories(
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """List all transaction categories with optional search"""
    query = db.query(models.TransactionCategory)

    if search:
        query = query.filter(
            models.TransactionCategory.name.ilike(f"%{search}%")
        )

    categories = query.offset(skip).limit(limit).all()
    return categories

@router.get("/{category_id}", response_model=schemas.TransactionCategoryResponse)
def get_category(
        category_id: str,
        db: Session = Depends(get_db)
):
    """Get a specific category by ID"""
    category = db.query(models.TransactionCategory).filter(
        models.TransactionCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category

@router.put("/{category_id}", response_model=schemas.TransactionCategoryResponse)
def update_category(
        category_id: str,
        category_update: schemas.TransactionCategoryCreate,
        db: Session = Depends(get_db)
):
    """Update an existing category"""
    existing_category = db.query(models.TransactionCategory).filter(
        models.TransactionCategory.id == category_id
    ).first()

    if not existing_category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Check if new name conflicts with another category
    if category_update.name != existing_category.name:
        name_conflict = db.query(models.TransactionCategory).filter(
            func.lower(models.TransactionCategory.name) == func.lower(category_update.name),
            models.TransactionCategory.id != category_id
        ).first()

        if name_conflict:
            raise HTTPException(
                status_code=400,
                detail="A category with this name already exists"
            )

    existing_category.name = category_update.name
    existing_category.description = category_update.description

    db.commit()
    db.refresh(existing_category)
    return existing_category

@router.delete("/{category_id}", response_model=schemas.TransactionCategoryResponse)
def delete_category(
        category_id: str,
        db: Session = Depends(get_db)
):
    """Delete a category if it's not being used"""
    category = db.query(models.TransactionCategory).filter(
        models.TransactionCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    # Check if category is being used in any transactions
    transaction_count = db.query(func.count(models.Transaction.id)).filter(
        models.Transaction.category_id == category_id
    ).scalar()

    if transaction_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete category: it is being used in {transaction_count} transactions"
        )

    db.delete(category)
    db.commit()
    return category

@router.get("/{category_id}/usage", response_model=schemas.CategoryUsageResponse)
def get_category_usage(
        category_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        db: Session = Depends(get_db)
):
    """Get usage statistics for a category"""
    category = db.query(models.TransactionCategory).filter(
        models.TransactionCategory.id == category_id
    ).first()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    query = db.query(models.Transaction).filter(
        models.Transaction.category_id == category_id
    )

    if start_date:
        query = query.filter(models.Transaction.created_at >= start_date)
    if end_date:
        query = query.filter(models.Transaction.created_at <= end_date)

    transactions = query.all()

    return {
        "category_id": category_id,
        "category_name": category.name,
        "total_transactions": len(transactions),
        "total_amount": sum(t.amount for t in transactions),
        "average_amount": sum(t.amount for t in transactions) / len(transactions) if transactions else 0,
        "last_used": max((t.created_at for t in transactions), default=None),
        "transactions": transactions
    }