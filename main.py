from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from database import engine
from models import Base
from routers import categories, events, sales, finance, meetings, auth, standalone_items
from dotenv import load_dotenv

import os

load_dotenv()

app = FastAPI(
    title="Events Management API",
    description="This API provides comprehensive management of events, including detailed analytics, revenue tracking, rescheduling, cancellations, and insights into capacity and sales performance.",
    version=os.getenv("VERSION"),
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    docs_url="/docs",
    redoc_url=None,
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

router = APIRouter()

@router.get("/")
def main_route():
    return {"name": "FinalistHub", "type": "api-server", "version": os.getenv("VERSION")}

@router.get("/health_check")
def health_check():
    return Response(status_code=204)

app.include_router(router, tags=["Main"])
app.include_router(events.router, prefix="/events", tags=["Events"])
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(sales.router, prefix="/sales", tags=["Sales"])
app.include_router(finance.router, prefix="/finance", tags=["Finance"])
app.include_router(meetings.router, prefix="/meetings", tags=["Meetings"])
app.include_router(standalone_items.router, prefix="/standalone", tags=["Standalone Items"])
app.include_router(categories.router)