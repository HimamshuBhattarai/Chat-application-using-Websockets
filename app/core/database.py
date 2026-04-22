import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, event
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import NullPool
from urllib.parse import urlparse

load_dotenv()

url = os.getenv("DATABASE_URL")


def create_database_if_not_exists():
    try:
        if "postgresql" in url:
            parsed = urlparse(url)
            db_name = parsed.path.lstrip('/')
            server_url = url.replace(f"/{db_name}", "/postgres")
            
            temp_engine = create_engine(server_url, poolclass=NullPool)
            with temp_engine.connect() as conn:
                result = conn.execute(
                    text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
                )
                if not result.fetchone():
                    conn.execute(text(f"CREATE DATABASE {db_name}"))
                    conn.commit()
                    print(f"✓ Database '{db_name}' created successfully")
                else:
                    print(f"✓ Database '{db_name}' already exists")
            temp_engine.dispose()
    except Exception as e:
        print(f"Note: Could not auto-create database: {e}")


create_database_if_not_exists()


engine = create_engine(
    url=url,
    poolclass=NullPool,
    echo_pool=False
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):

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