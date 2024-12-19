from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
import models, schemas
from database import get_db
from datetime import datetime

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
        db: Session = Depends(get_db)
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