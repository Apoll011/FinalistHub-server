from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import uuid
import base64
import models
from database import get_db
from datetime import datetime
from fastapi import Response
from sqlalchemy.sql.expression import extract

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

@router.patch("/{meeting_id}")
def update_meeting(
        meeting_id: str,
        meeting_data: dict,
        db: Session = Depends(get_db)
):
    db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    for key, value in meeting_data.items():
        setattr(db_meeting, key, value)

    db_meeting.updated_at = datetime.utcnow()
    db.commit()

    return {
        "id": db_meeting.id,
        "date": db_meeting.date,
        "time": db_meeting.time,
        "agenda": db_meeting.agenda,
        "updatedAt": db_meeting.updated_at
    }

@router.delete("/{meeting_id}")
def delete_meeting(
        meeting_id: str,
        db: Session = Depends(get_db)
):
    db_meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not db_meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    db.delete(db_meeting)
    db.commit()
    return Response(status_code=204)

@router.get("/upcoming")
def get_upcoming_meetings(db: Session = Depends(get_db)):
    current_date = datetime.utcnow().strftime("%Y-%m-%d")

    meetings = db.query(models.Meeting) \
        .filter(models.Meeting.date >= current_date) \
        .all()

    return {
        "meetings": [
            {
                "id": m.id,
                "date": m.date,
                "time": m.time,
                "location": m.location,
                "agenda": m.agenda,
                "status": m.status
            } for m in meetings
        ]
    }

@router.get("/{meeting_id}/minutes")
def get_meeting_minutes(
        meeting_id: str,
        db: Session = Depends(get_db)
):
    minutes = db.query(models.MeetingMinutes) \
        .filter(models.MeetingMinutes.meeting_id == meeting_id) \
        .first()

    if not minutes:
        raise HTTPException(status_code=404, detail="Minutes not found")

    file_data = base64.b64decode(minutes.file_data)

    return Response(
        content=file_data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{minutes.file_name}"'
        }
    )