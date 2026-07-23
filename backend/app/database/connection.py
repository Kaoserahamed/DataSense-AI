from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Create engine with proper configuration for SQLite
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

try:
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        echo=settings.DEBUG
    )
    
    # Test database connection
    with engine.connect() as conn:
        logger.info("Database connection established successfully")
        
except Exception as e:
    logger.error(f"Failed to connect to database: {str(e)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    try:
        # Import all models to ensure they're registered
        from app.models import Project, Dataset, DatasetMetadata, Chart, Report, ChatHistory
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
