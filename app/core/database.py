import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool

load_dotenv()

url = os.getenv("DATABASE_URL")

# Create engine with connection pooling and foreign key support
engine = create_engine(
    url=url,
    poolclass=NullPool,  # Disable connection pooling for better resource management
    echo_pool=False
)

# Enable foreign key constraints for SQLite (not needed for PostgreSQL but good practice)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign key constraints for SQLite databases"""
    if "sqlite" in url:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()