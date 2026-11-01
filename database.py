"""
Database Engine Configuration
Supports MySQL (production / specified target) with transparent SQLite fallback
for frictionless out-of-the-box local developer/atelier testing.
"""

import os
import logging
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from models import Base

logger = logging.getLogger("tailor_db")
logging.basicConfig(level=logging.INFO)

# Configurable DB URL
ENV_DB_URL = os.environ.get("DATABASE_URL", "").strip()
SQLITE_URL = "sqlite:///./bespoke_tailor.db"

active_dialect = "sqlite"

def create_db_engine():
    global active_dialect
    # If explicitly configured for MySQL
    if ENV_DB_URL and "mysql" in ENV_DB_URL.lower():
        try:
            logger.info("Attempting connection to MySQL: %s", ENV_DB_URL.split("@")[-1])
            test_engine = create_engine(
                ENV_DB_URL,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 3}
            )
            with test_engine.connect() as conn:
                logger.info("Successfully connected to MySQL database!")
            active_dialect = "mysql"
            return test_engine
        except Exception as e:
            logger.warning(
                "MySQL connection failed (%s). Falling back to local SQLite: %s",
                str(e), SQLITE_URL
            )
    
    # SQLite fallback
    active_dialect = "sqlite"
    sq_engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    
    @event.listens_for(sq_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return sq_engine

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created. Active dialect: %s", active_dialect)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
