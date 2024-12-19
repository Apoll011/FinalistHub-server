from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import uuid
import models, schemas
from database import get_db
from datetime import datetime

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

@router.post("/tickets", response_model=schemas.TicketSale)
def sell_tickets(
    sale: schemas.TicketSaleCreate,
    db: Session = Depends(get_db)
):
    # Get the ticket
    ticket = db.query(models.Ticket).filter(models.Ticket.id == sale.ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Get the event to check if it's still active
    event = db.query(models.Event).filter(models.Event.id == ticket.event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if event is still active
    if event.status != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Cannot sell tickets for {event.status} event"
        )

    # Check if ticket is still available
    if not ticket.available:
        raise HTTPException(
            status_code=400,
            detail="Tickets are no longer available for sale"
        )

    # Calculate total amount
    total_amount = ticket.price * sale.quantity

    # Create the ticket sale
    db_ticket_sale = models.TicketSale(
        id=str(uuid.uuid4()),
        ticket_id=sale.ticket_id,
        quantity=sale.quantity,
        total_amount=total_amount
    )

    db.add(db_ticket_sale)
    db.commit()
    db.refresh(db_ticket_sale)

    # Return formatted response
    return {
        "id": db_ticket_sale.id,
        "ticket_id": db_ticket_sale.ticket_id,
        "quantity": db_ticket_sale.quantity,
        "total_amount": db_ticket_sale.total_amount,
        "created_at": db_ticket_sale.created_at,
        "ticket_type": ticket.type,
        "event_name": event.name
    }

@router.get("/tickets/{event_id}/availability")
def check_ticket_availability(
    event_id: str,
    db: Session = Depends(get_db)
):
    # Get all tickets for the event
    tickets = db.query(models.Ticket)\
        .filter(models.Ticket.event_id == event_id)\
        .all()

    if not tickets:
        raise HTTPException(
            status_code=404,
            detail="No tickets found for this event"
        )

    # Get sales information for each ticket type
    availability = []
    for ticket in tickets:
        total_sold = db.query(func.sum(models.TicketSale.quantity))\
            .filter(models.TicketSale.ticket_id == ticket.id)\
            .scalar() or 0

        availability.append({
            "ticket_id": ticket.id,
            "ticket_type": ticket.type,
            "price": ticket.price,
            "available": ticket.available,
            "total_sold": total_sold
        })

    return {"tickets": availability}

@router.get("/tickets/sales-history/{event_id}")
def get_ticket_sales_history(
    event_id: str,
    db: Session = Depends(get_db)
):
    # Get all ticket sales for the event
    sales = db.query(models.TicketSale)\
        .join(models.Ticket)\
        .filter(models.Ticket.event_id == event_id)\
        .all()

    if not sales:
        return {
            "event_id": event_id,
            "total_sales": 0,
            "total_revenue": 0,
            "sales": []
        }

    # Format sales data
    sales_data = []
    total_revenue = 0

    for sale in sales:
        sales_data.append({
            "sale_id": sale.id,
            "ticket_type": sale.ticket.type,
            "quantity": sale.quantity,
            "total_amount": sale.total_amount,
            "customer_name": sale.customer_name,
            "customer_email": sale.customer_email,
            "purchase_date": sale.created_at
        })
        total_revenue += sale.total_amount

    return {
        "event_id": event_id,
        "total_sales": len(sales),
        "total_revenue": total_revenue,
        "sales": sales_data
    }