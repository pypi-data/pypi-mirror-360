from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from src.config import Config
from src.utils.logger import get_logger


DB_URL = f"mysql+mysqlconnector://{Config.DB_USERNAME}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}"

# Initialize logger for this module
logger = get_logger(__name__)   
try:
    engine = create_engine(DB_URL, pool_recycle=3600, echo=False) # echo=True for debugging SQL
    SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base = declarative_base()
    logger.info("Database engine and session created successfully.")
except Exception as e:
    logger.error(f"Error creating database engine or session: {e}", exc_info=True)
    # Depending on deployment, might want to raise to fail Lambda init
    raise

def get_db_session():
    """Provides a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        SessionLocal.remove() # Important for scoped_session 