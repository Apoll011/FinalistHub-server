from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.post("/stock-items", response_model=schemas.Sale)
def sell_stock_item(
        sale: schemas.SaleCreate,
        db: Session = Depends(get_db)
):
    db_item = db.query(models.Item).filter(models.Item.id == sale.item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    if db_item.quantity < sale.quantity_sold:
        raise HTTPException(status_code=400, detail="Insufficient stock")

    total_revenue = db_item.price * sale.quantity_sold

    db_sale = models.Sale(
        id=str(uuid.uuid4()),
        item_id=sale.item_id,
        quantity_sold=sale.quantity_sold,
        total_revenue=total_revenue
    )

    db_item.quantity -= sale.quantity_sold

    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale