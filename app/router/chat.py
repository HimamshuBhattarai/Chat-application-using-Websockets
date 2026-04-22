from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from core.database import get_db
from core.security import decode_token
from services.manager import manager
from schemas.models import Message, Room
import json

router = APIRouter(prefix="/chat", tags=["Chat"])


def get_messages_before(db: Session, room_id: int, cursor_id: int = None, limit: int = 20):
    query = db.query(Message).filter(Message.room_id == room_id)
    
    if cursor_id:
        query = query.filter(Message.id < cursor_id) 
    
    return query.order_by(Message.timestamp.desc()).limit(limit).all()

@router.websocket("/ws/{room_id}")
async def room_wise_chatting(websocket: WebSocket, room_id:int, token:str=Query(...), db: Session=Depends(get_db)):
    # Step 1:
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
    except HTTPException:
        await websocket.close(code=4401)
        return

    
    # Step 2:
    room = db.query(Room).filter(Room.id == room_id).first()
    if not room:
        await websocket.close(code=4004)
        return
    
    # Step 3:
    await manager.connect(str(room_id), websocket=websocket)
    
    # Step 4:
    # Step 4 — fetch history with cursor pagination
    messages = get_messages_before(db, room_id)
    for msg in reversed(messages):
        await websocket.send_text(json.dumps({
        "user_id": msg.user_id,
        "content": msg.content,
        "timestamp": str(msg.timestamp)
    }))


    # Step 5 — listen for messages
    try:
        while True:
            data = await websocket.receive_text()

            # save to DB
            new_message = Message(
                content=data,
                user_id=user_id,
                room_id=room_id
            )
            db.add(new_message)
            db.commit()
            db.refresh(new_message)

            # broadcast to everyone
            await manager.broadcast(
                str(room_id),
                json.dumps({
                    "user_id": user_id,
                    "content": data,
                    "timestamp": str(new_message.timestamp)
                }),
                websocket
            )

    # Step 6 — handle disconnect
    except WebSocketDisconnect:
        manager.disconnect(str(room_id), websocket)
    