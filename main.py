from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import events, sales, finance, meetings

app = FastAPI(title="Events Management API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(finance.router, prefix="/finance", tags=["Finance"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])