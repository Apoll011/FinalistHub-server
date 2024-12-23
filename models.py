from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="member")

class Event(Base):
    __tablename__ = "events"

    id = Column(String, primary_key=True)
    name = Column(String, index=True)
    date = Column(String)
    time = Column(String)
    location = Column(String)
    description = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)

    tickets = relationship("Ticket", back_populates="event")
    items = relationship("Item", back_populates="event")
    observations = relationship("Observation", back_populates="event")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True)
    event_id = Column(String, ForeignKey("events.id"))
    type = Column(String)
    price = Column(Float)
    available = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="tickets")

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True)
    event_id = Column(String, ForeignKey("events.id"), nullable=True)
    name = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="items")
    sales = relationship("Sale", back_populates="item")

class Sale(Base):
    __tablename__ = "sales"

    id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey("items.id"))
    quantity_sold = Column(Integer)
    total_revenue = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

    item = relationship("Item", back_populates="sales")

class Observation(Base):
    __tablename__ = "observations"

    id = Column(String, primary_key=True)
    event_id = Column(String, ForeignKey("events.id"))
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    event = relationship("Event", back_populates="observations")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True)
    type = Column(String)  # revenue or expense
    description = Column(Text)
    amount = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    event_id = Column(String, ForeignKey("events.id"), nullable=True)

class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(String, primary_key=True)
    date = Column(String)
    time = Column(String)
    location = Column(String)
    agenda = Column(Text)
    status = Column(String, default="scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

    minutes = relationship("MeetingMinutes", back_populates="meeting")

class MeetingMinutes(Base):
    __tablename__ = "meeting_minutes"

    id = Column(String, primary_key=True)
    meeting_id = Column(String, ForeignKey("meetings.id"))
    file_name = Column(String)
    file_size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    file_data = Column(Text)  # Store as base64 encoded string

    meeting = relationship("Meeting", back_populates="minutes")

class TicketSale(Base):
    __tablename__ = "ticket_sales"

    id = Column(String, primary_key=True)
    ticket_id = Column(String, ForeignKey("tickets.id"))
    quantity = Column(Integer)
    total_amount = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("Ticket", backref="sales")
