from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.security import get_current_user, require_role
from schemas.models import Message, Room
from schemas.pydantic_models import MessageResponse, RoomCreate

router = APIRouter(tags=["Rooms"])

@router.get("/rooms", response_model=List[dict])
def get_all_rooms(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get list of all available rooms"""
    rooms = db.query(Room).all()
    return [
        {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "created_at": room.created_at
        }
        for room in rooms
    ]

@router.post("/rooms", dependencies=[Depends(require_role("admin"))])
def create_room(payload: RoomCreate, db: Session = Depends(get_db)):
    # check if room name already exists
    if db.query(Room).filter(Room.name == payload.name).first():
        raise HTTPException(status_code=400, detail="Room already exists")
    
    room = Room(
        name=payload.name,
        description=payload.description
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room



def get_messages_before(db: Session, room_id: int, cursor_id: int = None, limit: int = 20):
    query = db.query(Message).filter(Message.room_id == room_id)
    if cursor_id:
        query = query.filter(Message.id < cursor_id)
    return query.order_by(Message.timestamp.desc()).limit(limit).all()

@router.get("/rooms/{room_id}/messages", response_model=List[MessageResponse])
def get_room_messages(
    room_id: int,
    cursor_id: int = None,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    messages = get_messages_before(db, room_id, cursor_id, limit)
    return list(reversed(messages))



