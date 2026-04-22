from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        # room_id -> list of connected websockets
        self.rooms: dict[str, list[WebSocket]] = {}

    async def connect(self, room_id: str, websocket: WebSocket):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
        self.rooms[room_id].append(websocket)

    def disconnect(self, room_id: str, websocket: WebSocket):
        self.rooms[room_id].remove(websocket)
        # clean up empty rooms
        if not self.rooms[room_id]:
            del self.rooms[room_id]

    async def broadcast(self, room_id: str, message: str, sender: WebSocket):
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                await connection.send_text(message)

# single instance shared across the app
manager = ConnectionManager()