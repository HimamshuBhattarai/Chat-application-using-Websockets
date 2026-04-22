# Chat Application

A real-time chat application built with FastAPI and WebSocket, featuring user authentication, room-based messaging, and admin controls.

**Group B Task Completed**: PostgreSQL Persistence & Data Modelling - See [Database Design](#database-design) section below.

## Features

- **User Authentication**: Signup and login with email/password
- **Real-time Chat**: WebSocket-based instant messaging
- **Chat Rooms**: Create and join different chat rooms
- **Role-based Access**: Admin and user roles
- **Message History**: Load previous messages with cursor pagination
- **Modern UI**: Responsive web interface

## Tech Stack

### Backend
- **Framework**: FastAPI
- **WebSocket**: For real-time messaging
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with argon2 password hashing
- **Server**: Uvicorn

### Frontend
- **HTML5/CSS3/JavaScript**: Vanilla frontend
- **WebSocket API**: For real-time communication

## Project Structure

```
chat-application/
├── frontend.html                 # Frontend UI
├── pyproject.toml               # Project dependencies
├── .env                         # Environment variables
├── README.md                    # This file
└── app/
    ├── main.py                  # FastAPI app setup
    ├── core/
    │   ├── database.py         # Database configuration
    │   └── security.py         # JWT and password hashing
    ├── router/
    │   ├── auth.py             # Authentication endpoints
    │   ├── chat.py             # WebSocket chat endpoint
    │   └── room_messages.py    # Room and message endpoints
    ├── schemas/
    │   ├── models.py           # SQLAlchemy models
    │   └── pydantic_models.py  # Request/response schemas
    └── services/
        └── manager.py          # WebSocket connection manager
```

## Database Design

### Overview
This application uses PostgreSQL with SQLAlchemy ORM to persist all application data. The database layer is designed with proper relationships, foreign key constraints, and efficient pagination for message history.

### Database Models

#### User Model
```python
class User(Base):
    __tablename__ = "users"
    id: int (Primary Key)
    username: str (Unique, Not Null)
    email: str (Unique, Not Null, Indexed)
    hashed_password: str (Not Null)
    role: str (Default: "user")  # "admin" or "user"
    is_active: bool (Default: True)
    messages: Relationship (One-to-Many with Message)
```

**Purpose**: Stores user accounts with authentication credentials and roles for RBAC.

#### Room Model
```python
class Room(Base):
    __tablename__ = "rooms"
    id: int (Primary Key)
    name: str (Not Null)
    description: str (Not Null)
    created_at: DateTime (Default: now)
    messages: Relationship (One-to-Many with Message)
```

**Purpose**: Represents chat rooms where multiple users can send messages.

#### Message Model
```python
class Message(Base):
    __tablename__ = "messages"
    id: int (Primary Key)
    content: str (Not Null)
    timestamp: DateTime (Default: now)
    user_id: int (Foreign Key → users.id, Not Null)
    room_id: int (Foreign Key → rooms.id, Not Null)
    user: Relationship (Many-to-One with User)
    room: Relationship (Many-to-One with Room)
```

**Purpose**: Persists all chat messages with references to the user and room.

### Relationships

The models implement the following relationships:
- **User ↔ Message**: One-to-Many (A user can send many messages)
- **Room ↔ Message**: One-to-Many (A room can contain many messages)
- **Cascade Behavior**: Deleting a user or room will cascade delete their associated messages

```python
# In User model
messages = relationship("Message", back_populates="user")

# In Room model
messages = relationship("Message", back_populates="room")

# In Message model
user = relationship("User", back_populates="messages")
room = relationship("Room", back_populates="messages")
```

### Foreign Key Constraints

All foreign keys are enforced at the database level:
```python
user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
room_id = Column(Integer, ForeignKey("rooms.id"), nullable=False)
```

The database.py module includes configuration to enforce foreign key constraints across different database backends:
- **PostgreSQL**: Constraints enforced natively
- **SQLite** (if used): Pragmas configured to enforce constraints

### Cursor-Based Pagination

Message history uses **cursor-based pagination** instead of offset-based pagination for better performance and consistency.

#### Implementation

```python
def get_messages_before(db: Session, room_id: int, cursor_id: int = None, limit: int = 20):
    """
    Fetch messages from a room using cursor-based pagination.
    
    Args:
        db: Database session
        room_id: Room ID to fetch messages from
        cursor_id: Message ID cursor (fetch messages with ID < cursor_id)
        limit: Number of messages to return (default 20)
    
    Returns:
        List of Message objects in ascending order by timestamp
    """
    query = db.query(Message).filter(Message.room_id == room_id)
    
    # Cursor-based filtering: only get messages before the cursor
    if cursor_id:
        query = query.filter(Message.id < cursor_id)
    
    # Order by timestamp descending, limit, then reverse for chronological order
    return query.order_by(Message.timestamp.desc()).limit(limit).all()
```

#### Why Cursor-Based Pagination?

1. **Performance**: No need to count total records or scan skipped rows
2. **Consistency**: Handles inserts/deletes between requests without showing duplicates
3. **Scalability**: Works efficiently with millions of messages
4. **User Experience**: Simpler UX with "load more" rather than page numbers

#### Usage Example

```bash
# Get first 20 messages from room 1
GET /rooms/1/messages

# Get next 20 messages (cursor_id = message ID of last loaded message)
GET /rooms/1/messages?cursor_id=15&limit=20
```

### Database Constraints

| Table | Column | Constraint | Type |
|-------|--------|-----------|------|
| users | id | Primary Key | Unique, Auto-increment |
| users | email | Unique | Ensures no duplicate emails |
| users | username | Unique | Ensures unique usernames |
| rooms | id | Primary Key | Unique, Auto-increment |
| messages | user_id | Foreign Key | References users.id |
| messages | room_id | Foreign Key | References rooms.id |

### Initialization

Tables are automatically created on application startup via SQLAlchemy's metadata system:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
```

If you need to reset the database:

```bash
# Drop all tables (caution: this deletes all data)
python -c "from app.core.database import Base, engine; Base.metadata.drop_all(bind=engine)"

# Recreate tables
python -c "from app.core.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- PostgreSQL database
- pip or uv package manager

### 1. Database Setup

Create a PostgreSQL database:
```sql
CREATE DATABASE chat_db;
```

### 2. Install Dependencies

```bash
# Using pip
pip install -e .

# Or using uv
uv pip install -e .
```

Install optional dependencies if needed:
```bash
pip install uvicorn[standard] 
```

### 3. Environment Configuration

Update the `.env` file with your settings:
```env
DATABASE_URL=postgresql://postgres:admin@localhost:5432/chat_db
SECRET_KEY=0d180304c872bccb9cc28b346d9874e23849aef3cf35e75e18e9c04e6f769ca7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRY_DAYS=10
```

### 4. Run the Backend

```bash
# From the app directory
cd app
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: `http://localhost:8000`

### 5. Access the Frontend

Open the frontend in your browser:
- Direct: Open `frontend.html` in your browser
- Local server: `python -m http.server 8080` and visit `http://localhost:8080/frontend.html`

## API Endpoints

### Authentication
- `POST /auth/signup` - Create a new account
  ```json
  {
    "username": "string",
    "email": "user@example.com",
    "password": "string",
    "role": "user|admin"
  }
  ```
- `POST /auth/login` - Login with email and password
  ```json
  {
    "email": "user@example.com",
    "password": "string"
  }
  ```
- `GET /auth/admin-only` - Admin-only endpoint (requires admin role)

### Rooms
- `POST /rooms` - Create a new room (admin only)
  ```json
  {
    "name": "string",
    "description": "string"
  }
  ```
- `GET /rooms/{room_id}/messages` - Get message history
  - Query params: `cursor_id` (int), `limit` (int, default 20)

### WebSocket Chat
- `WS /chat/{room_id}?token={token}` - Connect to a room
  - Send: Plain text message
  - Receive: JSON with `user_id`, `content`, `timestamp`

## Usage

### Creating an Account
1. Click "Sign Up" on the login page
2. Enter username, email, password, and select role
3. Account is created and you're automatically logged in

### Logging In
1. Enter email and password
2. Click "Login"

### Creating a Room (Admin Only)
1. Login with an admin account
2. Click "+ Create Room"
3. Enter room name and description
4. Click "Create"

### Joining a Room
1. Click on any room in the left sidebar
2. Message history loads automatically
3. Start typing and press Enter to send messages

### Real-time Chat
- Messages appear instantly for all connected users
- See message timestamps and user IDs
- Messages are persisted in the database

## Testing

### Test Credentials
Create test accounts through the signup flow or test with curl:

```bash
# Signup
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "role": "user"
  }'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# Create Room (as admin)
curl -X POST http://localhost:8000/rooms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "name": "test-room",
    "description": "Test room"
  }'
```

### WebSocket Testing with wscat
```bash
# Install wscat
npm install -g wscat

# Connect to room
wscat -c "ws://localhost:8000/chat/1?token=<your_token>"

# Send messages
> Hello everyone!
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

## Production Deployment

For production deployment:

1. Change `allow_origins` in CORS middleware to specific domains
2. Use a production database with proper backups
3. Set strong `SECRET_KEY` environment variable
4. Use HTTPS for frontend and WSS for WebSocket
5. Configure proper logging and monitoring
6. Use a production ASGI server like Gunicorn + Uvicorn

## Troubleshooting

### Database Connection Error
- Ensure PostgreSQL is running
- Check DATABASE_URL in .env file
- Verify database exists and credentials are correct

### WebSocket Connection Failed
- Check that backend server is running
- Verify token is valid and not expired
- Check browser console for detailed error messages

### CORS Errors
- Frontend and backend must be on different ports
- Verify CORS middleware is properly configured
- Check allowed origins in main.py

### Messages Not Appearing
- Check WebSocket connection is established
- Verify token is valid in browser DevTools
- Ensure room exists before connecting

## Performance Optimization

- Message history uses cursor pagination (limit 20 by default)
- WebSocket connections are lightweight
- Connection manager efficiently handles multiple rooms
- Consider caching frequently accessed rooms

## Future Enhancements

- [ ] Direct messaging between users
- [ ] User profiles and avatars
- [ ] Message reactions and editing
- [ ] File upload support
- [ ] Read receipts
- [ ] Typing indicators
- [ ] Full-text search
- [ ] Voice/video chat

## License

MIT License

## Contributing

Feel free to submit issues and enhancement requests!
