# Chat Application

A real-time chat application built with FastAPI, WebSocket, and PostgreSQL.

## Prerequisites

- Python 3.10+
- PostgreSQL
- Git

## Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/HimamshuBhattarai/Chat-application-using-Websockets
```

### 2. Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database

Create an empty PostgreSQL database:
```bash
createdb chat_db
```

Or use psql:
```sql
CREATE DATABASE chat_db;
```

**Note**: Tables will be created automatically when you run the server.

### 5. Configure Environment

Copy `.env.example` to `.env` and update with your database credentials:
```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/chat_db
SECRET_KEY=your_secret_key_here_at_least_32_characters_long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_DAYS=10
```

### 6. Run the Server

```bash
cd app
uvicorn main:app --reload
```

Server running at: `http://localhost:8000`

Frontend & API both available at the same URL.

## Project Structure

```
app/
├── main.py                  # FastAPI application
├── core/
│   ├── database.py         # Database configuration
│   └── security.py         # JWT and password hashing
├── router/
│   ├── auth.py             # Authentication endpoints
│   ├── chat.py             # WebSocket endpoint
│   └── room_messages.py    # Room and message endpoints
├── schemas/
│   ├── models.py           # SQLAlchemy models
│   └── pydantic_models.py  # Request/response schemas
└── services/
    └── manager.py          # WebSocket connection manager
```

## API Endpoints

- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `GET /rooms` - List all rooms
- `POST /rooms` - Create room (admin only)
- `GET /rooms/{room_id}/messages` - Get message history
- `WS /chat/ws/{room_id}` - WebSocket chat connection

## Environment Variables

See `.env.example` for all required variables.
```

## Key Features Explained

### JWT Authentication
- Tokens contain user ID and role
- Tokens expire after configured days
- Used for both HTTP and WebSocket connections

### WebSocket Manager
- Maintains connections per room
- Broadcasts messages to all users in a room
- Handles connection/disconnection automatically

### Cursor Pagination
- Message history uses cursor-based pagination
- Prevents fetching large amounts of data
- `cursor_id` points to the message ID boundary

### Role-based Access Control
- Admin role: Can create rooms
- User role: Can only view and chat
- Enforced at endpoint level with dependencies

## Security Considerations

1. **Password Hashing**: Argon2 algorithm used for secure hashing
2. **JWT Tokens**: Signed with SECRET_KEY, includes expiration
3. **CORS**: Currently allows all origins (update for production)
4. **Database**: Use environment variables for sensitive data