import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cyberguardian.db")

# For SQLite, we need to allow multithreading access if used across threads
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db():
    """
    FastAPI dependency that provides a transactional database session.
    Automatically closes the session after the request is finished.
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
