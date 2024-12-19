from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
import uuid
import models, schemas
from database import get_db
from datetime import datetime
from sqlalchemy.sql import func

router = APIRouter()

@router.post("/", response_model=schemas.Event)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    db_event = models.Event(
        id=str(uuid.uuid4()),
        **event.dict()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

@router.post("/{event_id}/tickets", response_model=schemas.Ticket)
def create_ticket(
    event_id: str,
    ticket: schemas.TicketCreate,
    db: Session = Depends(get_db)
):
    db_ticket = models.Ticket(
        id=str(uuid.uuid4()),
        event_id=event_id,
        **ticket.dict()
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket

@router.get("/calendar", response_model=List[schemas.Event])
def get_calendar(db: Session = Depends(get_db)):
    return db.query(models.Event).all()

@router.post("/{event_id}/items", response_model=schemas.Item)
def add_event_items(
        event_id: str,
        item: schemas.ItemCreate,
        db: Session = Depends(get_db)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_item = models.Item(
        id=str(uuid.uuid4()),
        event_id=event_id,
        **item.dict()
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.patch("/{event_id}/cancel")
def cancel_event(
        event_id: str,
        db: Session = Depends(get_db)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_event.status = "cancelled"
    db_event.cancelled_at = datetime.utcnow()
    db.commit()
    return {
        "id": db_event.id,
        "status": "cancelled",
        "cancelledAt": db_event.cancelled_at
    }

@router.patch("/{event_id}/reschedule")
def reschedule_event(
        event_id: str,
        new_schedule: dict,
        db: Session = Depends(get_db),
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_event.date = new_schedule.get("date")
    db_event.time = new_schedule.get("time")
    db_event.updated_at = datetime.utcnow()
    db.commit()

    return {
        "id": db_event.id,
        "date": db_event.date,
        "time": db_event.time,
        "updatedAt": db_event.updated_at
    }

@router.get("/{event_id}/details")
def get_event_details(
        event_id: str,
        db: Session = Depends(get_db)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get sales data
    sales_data = db.query(models.Sale) \
        .join(models.Item) \
        .filter(models.Item.event_id == event_id) \
        .all()

    total_revenue = sum(sale.total_revenue for sale in sales_data)
    items_sold = [
        {
            "name": sale.item.name,
            "quantity": sale.quantity_sold,
            "revenue": sale.total_revenue
        } for sale in sales_data
    ]

    # Get observations
    observations = [
        {
            "content": obs.content,
            "timestamp": obs.created_at
        } for obs in db_event.observations
    ]

    return {
        "id": db_event.id,
        "name": db_event.name,
        "date": db_event.date,
        "time": db_event.time,
        "location": db_event.location,
        "status": db_event.status,
        "sales": {
            "totalRevenue": total_revenue,
            "itemsSold": items_sold
        },
        "observations": observations
    }

@router.post("/{event_id}/observations")
def add_observation(
        event_id: str,
        observation: dict,
        db: Session = Depends(get_db)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_observation = models.Observation(
        id=str(uuid.uuid4()),
        event_id=event_id,
        content=observation.get("content")
    )
    db.add(db_observation)
    db.commit()
    db.refresh(db_observation)

    return {
        "id": db_observation.id,
        "eventId": event_id,
        "content": db_observation.content,
        "createdAt": db_observation.created_at
    }

@router.post("/{event_id}/close")
def close_event(
        event_id: str,
        db: Session = Depends(get_db)
):
    # Start database transaction
    try:
        # 1. Get the event and verify it's active
        event = db.query(models.Event).filter(models.Event.id == event_id).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != "active":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot close event that is already {event.status}"
            )

        # 2. Calculate ticket sales revenue
        ticket_sales = db.query(
            func.sum(models.TicketSale.total_amount).label('total')
        ).join(
            models.Ticket
        ).filter(
            models.Ticket.event_id == event_id
        ).first()

        ticket_revenue = ticket_sales.total or 0

        # 3. Calculate item sales revenue
        item_sales = db.query(
            func.sum(models.Sale.total_revenue).label('total')
        ).join(
            models.Item
        ).filter(
            models.Item.event_id == event_id
        ).first()

        item_revenue = item_sales.total or 0

        # 4. Create financial transactions for the revenues
        if ticket_revenue > 0:
            ticket_transaction = models.Transaction(
                id=str(uuid.uuid4()),
                type="revenue",
                description=f"Ticket sales revenue for event: {event.name}",
                amount=ticket_revenue,
                event_id=event_id
            )
            db.add(ticket_transaction)

        if item_revenue > 0:
            item_transaction = models.Transaction(
                id=str(uuid.uuid4()),
                type="revenue",
                description=f"Item sales revenue for event: {event.name}",
                amount=item_revenue,
                event_id=event_id
            )
            db.add(item_transaction)

        # 5. Update event status
        event.status = "closed"
        event.closed_at = datetime.utcnow()

        # 6. Generate financial summary
        financial_summary = {
            "ticket_revenue": ticket_revenue,
            "item_revenue": item_revenue,
            "total_revenue": ticket_revenue + item_revenue
        }

        # 7. Generate detailed report
        ticket_details = db.query(models.Ticket).filter(
            models.Ticket.event_id == event_id
        ).all()

        ticket_summary = []
        for ticket in ticket_details:
            sales = db.query(
                func.sum(models.TicketSale.quantity).label('quantity_sold'),
                func.sum(models.TicketSale.total_amount).label('revenue')
                ).filter(models.TicketSale.ticket_id == ticket.id).first()

            ticket_summary.append(
                {
                    "type": ticket.type,
                    "price": ticket.price,
                    "quantity_sold": sales.quantity_sold or 0,
                    "revenue": sales.revenue or 0
                }
            )

        item_details = db.query(models.Item).filter(
            models.Item.event_id == event_id
        ).all()

        item_summary = []
        for item in item_details:
            sales = db.query(
                func.sum(models.Sale.quantity_sold).label('quantity_sold'),
                func.sum(models.Sale.total_revenue).label('revenue')
                ).filter(models.Sale.item_id == item.id).first()

            item_summary.append(
                {
                    "name": item.name,
                    "price": item.price,
                    "quantity_sold": sales.quantity_sold or 0,
                    "revenue": sales.revenue or 0,
                    "remaining_stock": item.quantity
                }
            )

        # 8. Commit all changes
        db.commit()

        # 9. Return comprehensive closing report
        return {
            "event_id": event_id,
            "event_name": event.name,
            "status": "closed",
            "closed_at": event.closed_at,
            "financial_summary": financial_summary,
            "ticket_sales": {
                "total_revenue": ticket_revenue,
                "details": ticket_summary
            },
            "item_sales": {
                "total_revenue": item_revenue,
                "details": item_summary
            }
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error closing event: {str(e)}"
        )