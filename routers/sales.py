from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid
import models, schemas
from database import get_db
from datetime import datetime
from fastapi import Response
from sqlalchemy.sql.expression import extract

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

@router.post("/custom-item")
def sell_custom_item(
        item_data: dict,
        db: Session = Depends(get_db)
):
    total_revenue = item_data["price"] * item_data["quantitySold"]

    db_sale = models.Sale(
        id=str(uuid.uuid4()),
        name=item_data["name"],
        price=item_data["price"],
        quantity_sold=item_data["quantitySold"],
        total_revenue=total_revenue
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)

    return {
        "id": db_sale.id,
        "name": db_sale.name,
        "price": db_sale.price,
        "quantitySold": db_sale.quantity_sold,
        "totalRevenue": db_sale.total_revenue,
        "timestamp": db_sale.timestamp
    }

@router.post("/register-item", response_model=schemas.Item)
def register_item(
        item: schemas.ItemCreate,
        db: Session = Depends(get_db)
):
    db_item = models.Item(
        id=str(uuid.uuid4()),
        **item.dict()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/receipt/{event_id}")
def get_receipt(
        event_id: str,
        db: Session = Depends(get_db)
):
    sales = db.query(models.Sale) \
        .join(models.Item) \
        .filter(models.Item.event_id == event_id) \
        .all()

    if not sales:
        raise HTTPException(status_code=404, detail="No sales found for this event")

    items_sold = [
        {
            "name": sale.item.name,
            "quantity": sale.quantity_sold,
            "unitPrice": sale.item.price,
            "totalPrice": sale.total_revenue
        } for sale in sales
    ]

    total_sales = sum(sale.total_revenue for sale in sales)

    return {
        "eventId": event_id,
        "totalSales": total_sales,
        "itemsSold": items_sold,
        "timestamp": datetime.utcnow()
    }