from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.database import engine, Base
from router import auth, chat, room_messages
from contextlib import asynccontextmanager
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path


# Define base directory
BASE_DIR = Path(__file__).parent.parent

# create tables on startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Chat Application", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(room_messages.router)


# @app.get("/")
# def root():
#     return {"status": "Chat app is running"}

@app.get("/")
def root():
    return FileResponse(BASE_DIR / "static" / "frontend.html")