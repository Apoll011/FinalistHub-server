from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
import models, schemas
from database import get_db
from datetime import datetime
from typing import List, Optional

router = APIRouter()

@router.post("/items", response_model=schemas.StandaloneItem)
def create_standalone_item(
        item: schemas.StandaloneItemCreate,
        db: Session = Depends(get_db)
):
    """Create a new standalone item"""
    db_item = models.StandaloneItem(
        id=str(uuid.uuid4()),
        status=schemas.ItemStatus.active,
        **item.dict()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/items", response_model=List[schemas.StandaloneItem])
def get_items(
        status: Optional[schemas.ItemStatus] = None,
        db: Session = Depends(get_db)
):
    """Get all standalone items with optional status filter"""
    query = db.query(models.StandaloneItem)
    if status:
        query = query.filter(models.StandaloneItem.status == status)
    return query.all()

@router.get("/items/{item_id}", response_model=schemas.StandaloneItem)
def get_item(
        item_id: str,
        db: Session = Depends(get_db)
):
    """Get a specific standalone item by ID"""
    item = db.query(models.StandaloneItem).filter(
        models.StandaloneItem.id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/items/{item_id}", response_model=schemas.StandaloneItem)
def update_item(
        item_id: str,
        item_update: schemas.StandaloneItemUpdate,
        db: Session = Depends(get_db)
):
    """Update a standalone item's details"""
    db_item = db.query(models.StandaloneItem).filter(
        models.StandaloneItem.id == item_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(db_item, key, value)

    db.commit()
    db.refresh(db_item)
    return db_item

@router.post("/items/{item_id}/sell", response_model=schemas.StandaloneItemSale)
def sell_item(
        item_id: str,
        sale: schemas.StandaloneItemSaleCreate,
        db: Session = Depends(get_db)
):
    """Record a sale for a standalone item"""
    db_item = db.query(models.StandaloneItem).filter(
        models.StandaloneItem.id == item_id
    ).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item.status != schemas.ItemStatus.active:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot sell {db_item.status} item"
        )

    if db_item.quantity < sale.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    total_amount = db_item.price * sale.quantity

    db_sale = models.StandaloneItemSale(
        id=str(uuid.uuid4()),
        item_id=item_id,
        quantity=sale.quantity,
        total_amount=total_amount,
        payment_method=sale.payment_method
    )

    db_item.quantity -= sale.quantity

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    return db_sale

@router.post("/items/{item_id}/close", status_code=204)
def close_item(
        item_id: str,
        close_request: schemas.CloseItemRequest,
        db: Session = Depends(get_db)
):
    """Close an item and create a transaction for all its sales"""
    try:
        db_item = db.query(models.StandaloneItem).filter(
            models.StandaloneItem.id == item_id
        ).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")

        if db_item.status != schemas.ItemStatus.active:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot close item that is already {db_item.status}"
            )

        # Calculate total sales
        sales_total = db.query(
            func.sum(models.StandaloneItemSale.total_amount).label('total')
        ).filter(
            models.StandaloneItemSale.item_id == item_id
        ).first()

        total_revenue = sales_total.total or 0

        if total_revenue > 0:
            # Create transaction record
            transaction = models.Transaction(
                id=str(uuid.uuid4()),
                type=schemas.TransactionType.REVENUE,
                amount=total_revenue,
                description=f"Sales for item: {db_item.name}",
                payment_method=schemas.PaymentMethod.CASH,
                to_account_id=close_request.to_account_id,
                created_by=close_request.user_id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Update account balance
            account = db.query(models.Account).filter_by(
                id=transaction.to_account_id
            ).first()
            account.current_balance += transaction.amount

            db.add(transaction)

        # Update item status
        db_item.status = schemas.ItemStatus.closed
        db_item.closed_at = datetime.utcnow()

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error closing item: {str(e)}"
        )

@router.get("/items/{item_id}/report", response_model=schemas.StandaloneItemReport)
def get_item_report(
        item_id: str,
        db: Session = Depends(get_db)
):
    """Get a sales report for a specific item"""
    item = db.query(models.StandaloneItem).filter(
        models.StandaloneItem.id == item_id
    ).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Get sales data
    sales = db.query(
        func.sum(models.StandaloneItemSale.quantity).label('total_quantity'),
        func.sum(models.StandaloneItemSale.total_amount).label('total_revenue')
    ).filter(
        models.StandaloneItemSale.item_id == item_id
    ).first()

    # Get sales by payment method
    sales_by_method = db.query(
        models.StandaloneItemSale.payment_method,
        func.sum(models.StandaloneItemSale.total_amount).label('total')
    ).filter(
        models.StandaloneItemSale.item_id == item_id
    ).group_by(
        models.StandaloneItemSale.payment_method
    ).all()

    return {
        "item_id": item_id,
        "name": item.name,
        "status": item.status,
        "current_quantity": item.quantity,
        "price": item.price,
        "sales_summary": {
            "total_quantity_sold": sales.total_quantity or 0,
            "total_revenue": sales.total_revenue or 0,
            "sales_by_payment_method": [
                {
                    "method": method,
                    "amount": total
                } for method, total in sales_by_method
            ]
        }
    }