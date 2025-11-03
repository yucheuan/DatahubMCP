from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
from urllib.parse import quote_plus
from contextlib import contextmanager
import os

# Load environment variables from .env file
load_dotenv()

# Get database configuration from environment variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# Construct database URL with URL-encoded password
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Create engine and session with connection pooling and health checks
engine = create_engine(
    DATABASE_URL, 
    echo=False,
    pool_pre_ping=True,  # Test connections before using them
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,         # Number of connections to maintain
    max_overflow=10,     # Maximum number of connections beyond pool_size
    connect_args={
        'connect_timeout': 10  # Connection timeout in seconds
    }
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Context manager for database sessions
@contextmanager
def get_db_session():
    """Context manager for database sessions. Automatically handles cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()