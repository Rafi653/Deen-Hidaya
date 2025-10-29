"""
Database connection and session management
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "deen_hidaya")
POSTGRES_USER = os.getenv("POSTGRES_USER", "deen_user")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "change_this_password")

# Create database URL
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    pool_size=5,
    max_overflow=10
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Get database session.
    
    Usage:
        db = get_db()
        try:
            # Use db session
            pass
        finally:
            db.close()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def test_connection():
    """Test database connection."""
    try:
        connection = engine.connect()
        result = connection.execute(text("SELECT 1"))
        connection.close()
        print("✓ Database connection successful")
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False
