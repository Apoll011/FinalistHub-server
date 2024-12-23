from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routers import events, sales, finance, meetings, auth

app = FastAPI(
    title="Events Management API",
    description="This API provides comprehensive management of events, including detailed analytics, revenue tracking, rescheduling, cancellations, and insights into capacity and sales performance.",
    version="1.0.0",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(finance.router, prefix="/finance", tags=["Finance"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])