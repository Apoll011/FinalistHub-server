from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func, text
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
        print("Hello", sale.item_id)
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
    if event.status != schemas.EventStatus.active:
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

@router.get("/tickets/{event_id}/availability", response_model=schemas.TicketAvailabilityResponse)
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

@router.get("/tickets/{event_id}/sales-history/", response_model=schemas.TicketSalesHistoryResponse)
def get_ticket_sales_history(
    event_id: str,
    db: Session = Depends(get_db)
):
    """Get all ticket sales for the event"""
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
            "purchase_date": sale.created_at
        })
        total_revenue += sale.total_amount

    return {
        "event_id": event_id,
        "total_sales": len(sales),
        "total_revenue": total_revenue,
        "sales": sales_data
    }

@router.get("/top-selling-items/{event_id}", response_model=schemas.TopItemsResponse)
def get_top_selling_items(
        event_id: str,
        limit: int = 10,
        db: Session = Depends(get_db)
):
    """Get top selling items by quantity and revenue for a specific event."""
    query = db.query(
        models.Item.name,
        func.sum(models.Sale.quantity_sold).label('total_quantity'),
        func.sum(models.Sale.total_revenue).label('total_revenue')
    ).join(models.Item, models.Sale.item_id == models.Item.id) \
        .filter(models.Item.event_id == event_id)

    top_items = query.group_by(models.Item.name) \
        .order_by(text('total_revenue DESC')) \
        .limit(limit) \
        .all()

    return {
        "items": [
            {
                "name": item.name,
                "total_quantity": item.total_quantity,
                "total_revenue": item.total_revenue
            } for item in top_items
        ]
    }



@router.post("/bulk-sale", response_model=schemas.BulkSaleResponse)
def create_bulk_sale(
        items: List[schemas.SaleCreate],
        db: Session = Depends(get_db)
):
    """Create multiple sales in a single transaction"""
    total_revenue = 0
    sales_records = []

    for item_sale in items:
        item = db.query(models.Item) \
            .filter(models.Item.id == item_sale.item_id) \
            .first()

        if not item:
            raise HTTPException(status_code=404, detail=f"Item {item_sale.item_id} not found")

        if item.quantity < item_sale.quantity_sold:
            raise HTTPException(status_code=400, detail=f"Insufficient stock for item {item.name}")

        sale_revenue = item.price * item_sale

        sale = models.Sale(
            id=str(uuid.uuid4()),
            item_id=item.id,
            quantity_sold=item_sale.quantity_sold,
            total_revenue=sale_revenue
        )

        item.quantity -= item_sale.quantity_sold
        total_revenue += sale_revenue
        sales_records.append(sale)
        db.add(sale)

    db.commit()

    return {
        "total_revenue": total_revenue,
        "sales_count": len(sales_records)
    }

@router.get("/inventory-alerts/{event_id}", response_model=schemas.InventoryAlertResponse)
def get_inventory_alerts(
        event_id: str,
        threshold: int = 10,
        db: Session = Depends(get_db)
):
    """Get items with low inventory for a specific event."""
    low_stock_items = db.query(models.Item) \
        .filter(models.Item.event_id == event_id) \
        .filter(models.Item.quantity <= threshold) \
        .all()

    return {
        "low_stock_items": [
            {
                "id": item.id,
                "name": item.name,
                "current_quantity": item.quantity,
                "price": item.price
            } for item in low_stock_items
        ]
    }