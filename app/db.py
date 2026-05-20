"""
Database connection and session management using SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

from config import settings

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # Avoid connection issues in containers
    echo=settings.debug,
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Session:
    """
    Get a new database session.
    
    Returns:
        Session: A SQLAlchemy session instance.
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        raise


def close_db_session(db: Session) -> None:
    """
    Close a database session.
    
    Args:
        db (Session): The session to close.
    """
    if db:
        db.close()


def init_db() -> bool:
    """
    Initialize the database by executing seed.sql.
    
    Returns:
        bool: True if initialization succeeded, False otherwise.
    """
    try:
        import os
        seed_file = os.path.join(os.path.dirname(__file__), "sql", "seed.sql")
        
        if not os.path.exists(seed_file):
            logger.warning(f"Seed file not found at {seed_file}")
            return False
        
        with open(seed_file, "r") as f:
            sql_script = f.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
        
        with engine.begin() as connection:
            for statement in statements:
                if statement.strip():
                    connection.execute(statement)
        
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False
