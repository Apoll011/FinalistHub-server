from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import uuid
import base64
from .. import models, schemas
from ..database import get_db

router = APIRouter()

@router.post("/")
def create_meeting(
        date: str,
        time: str,
        location: str,
        agenda: str,
        db: Session = Depends(get_db)
):
    meeting = models.Meeting(
        id=str(uuid.uuid4()),
        date=date,
        time=time,
        location=location,
        agenda=agenda
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)
    return meeting

@router.post("/{meeting_id}/minutes")
async def upload_minutes(
        meeting_id: str,
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    contents = await file.read()
    file_data = base64.b64encode(contents).decode()

    minutes = models.MeetingMinutes(
        id=str(uuid.uuid4()),
        meeting_id=meeting_id,
        file_name=file.filename,
        file_size=len(contents),
        file_data=file_data
    )
    db.add(minutes)
    db.commit()
    db.refresh(minutes)
    return {
        "id": minutes.id,
        "meeting_id": minutes.meeting_id,
        "file_name": minutes.file_name,
        "file_size": minutes.file_size,
        "uploaded_at": minutes.uploaded_at
    }