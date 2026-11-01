"""
Database Engine Configuration
Supports MySQL (production / specified target) with transparent SQLite fallback
for frictionless out-of-the-box local developer/atelier testing and Vercel serverless.
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

# On Vercel serverless functions, the root filesystem is read-only. Only /tmp is writable.
if os.environ.get("VERCEL"):
    SQLITE_URL = "sqlite:////tmp/bespoke_tailor.db"
else:
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

def auto_seed_if_empty():
    from models import Customer, Measurement, Order
    from calculator import TailorYardageCalculator
    db = SessionLocal()
    try:
        if db.query(Customer).first() is None:
            logger.info("Auto-seeding initial atelier data for cold start...")
            c1 = Customer(
                name="Vikram Singhania",
                phone="+91 98201 44892",
                email="vikram.singhania@ateliersavile.in",
                city="Mumbai (Marine Lines)",
                notes="Trial #2 in progress. Jhuka hua kandha (-0.5\" right shoulder drop), Jodhpuri padded chest pad factored."
            )
            db.add(c1)
            db.flush()

            m1 = Measurement(
                customer_id=c1.id,
                unit="in",
                neck=16.5, shoulder=18.2, chest=41.5, bicep=14.0, wrist=7.5,
                waist=34.0, hip=40.0, inseam=32.5, outseam=41.0, thigh=24.5, calf=15.5,
                jacket_length=30.0, shirt_length=29.5, sleeve_length=25.0,
                ease_preset="barabar",
                posture_notes="Right shoulder drop -0.5 inch. Erect stance, hollow lower back."
            )
            db.add(m1)
            db.flush()

            calc1 = TailorYardageCalculator.calculate(
                garment_style="bandhgala",
                measurements={"chest": 41.5, "waist": 34.0, "hip": 40.0, "jacket_length": 30.0, "sleeve_length": 25.0, "outseam": 41.0},
                fabric_width_inches=58.0, pattern_type="plain", fit_preset="barabar"
            )

            o1 = Order(
                order_no="BY-2024-89",
                customer_id=c1.id,
                measurement_id=m1.id,
                garment_style="Bandhgala & Jodhpuri Trouser",
                fabric_name="Raymond Super 120s Merino Wool (58\" Bada Pana)",
                fabric_mill="Raymond Savile Collection India",
                fabric_width_in=58.0,
                fabric_pattern="plain",
                total_meters=calc1["total_meters"],
                total_yards=calc1["total_yards"],
                total_gaj=calc1["total_gaj"],
                jacket_meters=calc1["breakdown"]["jacket_meters"],
                trouser_meters=calc1["breakdown"]["trouser_meters"],
                lining_meters=calc1["breakdown"]["lining_meters"],
                canvas_meters=calc1["breakdown"]["canvas_meters"],
                fabric_cost=8452.50, stitching_cost=6500.00, total_bill=16935.00,
                advance_paid=10000.00, balance_amount=6935.00,
                status="Trial Scheduled", trial_stage="Trial #2",
                trial_date="Kal Subah 11:30 AM (12 Nov 2024)",
                delivery_date="18 Nov 2024",
                senior_cutter="Master V. Sharma",
                workshop_section="Marine Lines Section"
            )
            db.add(o1)

            c2 = Customer(name="Rajesh Mehra", phone="+91 98190 22341", city="South Mumbai")
            db.add(c2)
            db.flush()

            calc2 = TailorYardageCalculator.calculate(
                garment_style="suit_2pc",
                measurements={"chest": 43.0, "waist": 36.0, "hip": 42.0, "jacket_length": 30.5, "sleeve_length": 25.5, "outseam": 40.5},
                fabric_width_inches=58.0, pattern_type="stripe"
            )

            o2 = Order(
                order_no="BY-2024-90",
                customer_id=c2.id,
                garment_style="2-Piece Bespoke Lounge Suit",
                fabric_name="Scabal Super 140s Navy Pinstripe",
                fabric_mill="Scabal Savile Row",
                fabric_width_in=58.0, fabric_pattern="stripe",
                total_meters=calc2["total_meters"], total_yards=calc2["total_yards"], total_gaj=calc2["total_gaj"],
                jacket_meters=calc2["breakdown"]["jacket_meters"], trouser_meters=calc2["breakdown"]["trouser_meters"],
                lining_meters=calc2["breakdown"]["lining_meters"], canvas_meters=calc2["breakdown"]["canvas_meters"],
                fabric_cost=14200.00, stitching_cost=8500.00, total_bill=22700.00,
                advance_paid=15000.00, balance_amount=7700.00,
                status="Cutting", trial_stage="Basting", trial_date="15 Nov 2024"
            )
            db.add(o2)

            db.commit()
            logger.info("Auto-seed completed.")
    except Exception as e:
        logger.warning("Auto-seed skipped/failed: %s", str(e))
        db.rollback()
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created. Active dialect: %s", active_dialect)
    auto_seed_if_empty()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
