from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid
from .. import models, schemas
from ..database import get_db

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