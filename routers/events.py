from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
import models, schemas
from database import get_db
from datetime import datetime, timedelta
from sqlalchemy.sql import func
from sqlalchemy import or_, text
from typing import Dict, Optional, List

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

@router.get("/{event_id}/", response_model=schemas.Event)
def get_event_data(
    event_id: str,
    db: Session = Depends(get_db)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()

    return db_event


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

@router.patch("/{event_id}/cancel", response_model=schemas.CancelEventResponse)
def cancel_event(
        event_id: str,
        db: Session = Depends(get_db)
):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not db_event:
        raise HTTPException(status_code=404, detail="Event not found")

    db_event.status = "cancelled"
    db_event.closed_at = datetime.utcnow()
    db.commit()
    return {
        "id": db_event.id,
        "status": "cancelled",
        "cancelledAt": db_event.closed_at
    }

@router.patch("/{event_id}/reschedule", response_model=schemas.RescheduleEventResponse)
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
    db.commit()

    return {
        "id": db_event.id,
        "date": db_event.date,
        "time": db_event.time,
    }

@router.get("/{event_id}/details", response_model=schemas.EventDetailsResponse)
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
    ticket_sales = db.query(
        func.sum(models.TicketSale.total_amount).label('total')
    ).join(
        models.Ticket
    ).filter(
        models.Ticket.event_id == event_id
    ).first()

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

    ticket_revenue = ticket_sales.total or 0

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
            "total_revenue": total_revenue + tickes_sales,
            "tickets_sold": ticket_summary,
            "items_sold": items_sold
        },
        "observations": observations
    }

@router.post("/{event_id}/observations", response_model=schemas.ObservationResponse)
def add_observation(
        event_id: str,
        observation: schemas.ObservationInput,
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

@router.get("/{event_id}/tickets", response_model=List[schemas.Ticket])
def get_event_tickets(
        event_id: str,
        db: Session = Depends(get_db)
):
    tickets = db.query(models.Ticket) \
        .filter(models.Ticket.event_id == event_id) \
        .all()

    if not tickets:
        raise HTTPException(
            status_code=404,
            detail="No tickets found for this event"
        )

    return tickets

@router.get("/{event_id}/items", response_model=List[schemas.Item])
def get_event_items(
        event_id: str,
        db: Session = Depends(get_db)
):
    items = db.query(models.Item) \
        .filter(models.Item.event_id == event_id) \
        .all()

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No items found for this event"
        )

    return items

@router.get("/statistics", response_model=schemas.EventStatisticsResponse)
def get_events_statistics(
        start_date: Optional[str] = f"{datetime.now().year}-1-1",
        end_date: Optional[str] = f"{datetime.now().year}-12-31",
        db: Session = Depends(get_db)
):
    """Get statistical overview of all events within a date range"""
    query = db.query(models.Event)

    if start_date:
        query = query.filter(models.Event.date >= start_date)
    if end_date:
        query = query.filter(models.Event.date <= end_date)

    events = query.all()

    total_events = len(events)
    active_events = len([e for e in events if e.status == "active"])
    closed_events = len([e for e in events if e.status == "closed"])
    cancelled_events = len([e for e in events if e.status == "cancelled"])

    # Calculate total revenue from closed events
    total_revenue = 0
    for event in events:
        if event.status == "closed":
            # Sum ticket sales
            ticket_revenue = db.query(func.sum(models.TicketSale.total_amount)) \
                                 .join(models.Ticket) \
                                 .filter(models.Ticket.event_id == event.id) \
                                 .scalar() or 0

            # Sum item sales
            item_revenue = db.query(func.sum(models.Sale.total_revenue)) \
                               .join(models.Item) \
                               .filter(models.Item.event_id == event.id) \
                               .scalar() or 0

            total_revenue += ticket_revenue + item_revenue

    return {
        "total_events": total_events,
        "active_events": active_events,
        "closed_events": closed_events,
        "cancelled_events": cancelled_events,
        "total_revenue": total_revenue,
        "date_range": {
            "start": start_date,
            "end": end_date
        }
    }

@router.post("/{event_id}/duplicate", response_model=schemas.DuplicateEventResponse)
def duplicate_event(
        event_id: str,
        new_date: str,
        new_time: str,
        db: Session = Depends(get_db)
):
    """Duplicate an existing event with its tickets and items"""
    # Get original event
    original_event = db.query(models.Event) \
        .filter(models.Event.id == event_id) \
        .first()

    if not original_event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Create new event
    new_event = models.Event(
        id=str(uuid.uuid4()),
        name=f"{original_event.name} (Copy)",
        date=new_date,
        time=new_time,
        location=original_event.location,
        description=original_event.description,
        status="active"
    )
    db.add(new_event)

    # Duplicate tickets
    original_tickets = db.query(models.Ticket) \
        .filter(models.Ticket.event_id == event_id) \
        .all()

    for ticket in original_tickets:
        new_ticket = models.Ticket(
            id=str(uuid.uuid4()),
            event_id=new_event.id,
            type=ticket.type,
            price=ticket.price,
            available=True
        )
        db.add(new_ticket)

    # Duplicate items
    original_items = db.query(models.Item) \
        .filter(models.Item.event_id == event_id) \
        .all()

    for item in original_items:
        new_item = models.Item(
            id=str(uuid.uuid4()),
            event_id=new_event.id,
            name=item.name,
            quantity=item.quantity,
            price=item.price
        )
        db.add(new_item)

    db.commit()
    db.refresh(new_event)

    return {
        "new_event_id": new_event.id,
        "name": new_event.name,
        "date": new_event.date,
        "time": new_event.time
    }

@router.get("/search", response_model=schemas.SearchEventsResponse)
def search_events(
        query: str,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Search events by name, description, or location with optional filters"""
    search = f"%{query}%"

    # Base query
    events_query = db.query(models.Event).filter(
        or_(
            models.Event.name.ilike(search),
            models.Event.description.ilike(search),
            models.Event.location.ilike(search)
        )
    )

    # Apply filters
    if status:
        events_query = events_query.filter(models.Event.status == status)
    if start_date:
        events_query = events_query.filter(models.Event.date >= start_date)
    if end_date:
        events_query = events_query.filter(models.Event.date <= end_date)

    # Execute query
    events = events_query.all()

    return {
        "total_results": len(events),
        "events": [
            {
                "id": event.id,
                "name": event.name,
                "date": event.date,
                "time": event.time,
                "location": event.location,
                "status": event.status
            } for event in events
        ]
    }

@router.get("/trending", response_model=schemas.EventTrendingResponse)
def get_trending_events(
        days: int = 30,
        limit: int = 5,
        db: Session = Depends(get_db)
):
    """Get trending events based on ticket sales"""
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    query = db.query(
        models.Event,
        func.count(models.TicketSale.id).label('ticket_count')
    ).join(models.Ticket) \
        .join(models.TicketSale) \
        .filter(
        models.Event.status == "active",
        models.TicketSale.created_at >= cutoff_date
    ).group_by(models.Event) \
        .order_by(text('ticket_count DESC')) \
        .limit(limit)

    trending = query.all()

    return {
        "trending_events": [
            {
                "id": event.Event.id,
                "name": event.Event.name,
                "date": event.Event.date,
                "ticket_sales": event.ticket_count
            } for event in trending
        ]
    }

@router.get("/revenue-ranking", response_model=schemas.RevenueRankingResponse)
def get_event_revenue_ranking(
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get events ranked by total revenue"""
    query = db.query(
        models.Event,
        func.coalesce(func.sum(models.TicketSale.total_amount), 0).label('ticket_revenue'),
        func.coalesce(func.sum(models.Sale.total_revenue), 0).label('item_revenue')
    ).outerjoin(models.Ticket) \
        .outerjoin(models.TicketSale) \
        .outerjoin(models.Item) \
        .outerjoin(models.Sale)

    if start_date:
        query = query.filter(models.Event.date >= start_date)
    if end_date:
        query = query.filter(models.Event.date <= end_date)

    events = query.group_by(models.Event) \
        .order_by(text('ticket_revenue + item_revenue DESC')) \
        .all()

    return {
        "events": [
            {
                "id": event.Event.id,
                "name": event.Event.name,
                "date": event.Event.date,
                "ticket_revenue": event.ticket_revenue,
                "item_revenue": event.item_revenue,
                "total_revenue": event.ticket_revenue + event.item_revenue
            } for event in events
        ]
    }

@router.get("/capacity-analysis", response_model=schemas.CapacityAnalysisResponse)
def get_capacity_analysis(
        db: Session = Depends(get_db)
):
    """Analyze venue capacity utilization"""
    events = db.query(models.Event) \
        .filter(models.Event.status == "active") \
        .all()

    analysis = []
    for event in events:
        tickets_sold = db.query(func.sum(models.TicketSale.quantity)) \
                           .join(models.Ticket) \
                           .filter(models.Ticket.event_id == event.id) \
                           .scalar() or 0

        analysis.append(
            {
                "event_id": event.id,
                "name": event.name,
                "date": event.date,
                "tickets_sold": tickets_sold,
                "status": event.status
            }
        )

    return {
        "capacity_analysis": analysis
    }

@router.get("/attendance-forecast", response_model=schemas.EventForecastResponse)
def get_attendance_forecast(
        event_id: str,
        db: Session = Depends(get_db)
):
    """Generate attendance forecast based on historical data and current sales"""
    event = db.query(models.Event) \
        .filter(models.Event.id == event_id) \
        .first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get current ticket sales
    current_sales = db.query(models.TicketSale) \
        .filter(models.TicketSale.event_id == event_id) \
        .count()  # Simple count of sales

    # Retrieve historical attendance data
    historical_data = db.query(models.Attendance) \
        .filter(models.Attendance.event_id == event_id) \
        .all()

    if not historical_data:
        raise HTTPException(status_code=404, detail="No historical attendance data available")

    # Use a simple average of historical attendance as a forecast
    historical_counts = [data.count for data in historical_data]
    average_attendance = sum(historical_counts) / len(historical_counts)

    # Predict attendance as average of historical counts
    forecasted_attendance = int(average_attendance)

    # Return the forecasted attendance
    return {
        "event_id": event_id,
        "current_sales": current_sales,
        "predicted_attendance": forecasted_attendance,
        "historical_data": [{"date": data.date, "count": data.count} for data in historical_data],
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

        if item_revenue < 0:
            item_transaction = models.Transaction(
                id=str(uuid.uuid4()),
                type="expense",
                description=f"Item sales expense for event: {event.name}",
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