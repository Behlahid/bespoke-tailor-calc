"""
Database Models for Bespoke Tailoring & Yardage System
Enforces referential integrity, ON DELETE CASCADE, and deterministic auditing.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False, index=True)
    phone = Column(String(30), nullable=True, index=True)
    email = Column(String(120), nullable=True)
    city = Column(String(80), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships with CASCADE
    measurements = relationship("Measurement", back_populates="customer", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="customer", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "phone": self.phone or "",
            "email": self.email or "",
            "city": self.city or "",
            "notes": self.notes or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "measurement_count": len(self.measurements) if self.measurements else 0,
            "order_count": len(self.orders) if self.orders else 0,
        }

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    unit = Column(String(10), default="in", nullable=False) # 'in' or 'cm'

    # Anatomical Points (in inches by default)
    neck = Column(Float, default=16.5)
    shoulder = Column(Float, default=18.2)
    chest = Column(Float, default=41.5)
    bicep = Column(Float, default=14.0)
    wrist = Column(Float, default=7.5)
    waist = Column(Float, default=34.0)
    hip = Column(Float, default=40.0)
    inseam = Column(Float, default=32.5)
    outseam = Column(Float, default=41.0)
    thigh = Column(Float, default=24.0)
    calf = Column(Float, default=15.5)
    jacket_length = Column(Float, default=30.0)
    shirt_length = Column(Float, default=29.5)
    sleeve_length = Column(Float, default=25.0)

    ease_preset = Column(String(20), default="barabar", nullable=False) # chust, barabar, dhila
    posture_notes = Column(Text, nullable=True) # e.g. "Jhuka hua kandha (-0.5 right shoulder drop)"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="measurements")
    orders = relationship("Order", back_populates="measurement")

    def to_dict(self):
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "unit": self.unit,
            "neck": self.neck,
            "shoulder": self.shoulder,
            "chest": self.chest,
            "bicep": self.bicep,
            "wrist": self.wrist,
            "waist": self.waist,
            "hip": self.hip,
            "inseam": self.inseam,
            "outseam": self.outseam,
            "thigh": self.thigh,
            "calf": self.calf,
            "jacket_length": self.jacket_length,
            "shirt_length": self.shirt_length,
            "sleeve_length": self.sleeve_length,
            "ease_preset": self.ease_preset,
            "posture_notes": self.posture_notes or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_no = Column(String(40), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    measurement_id = Column(Integer, ForeignKey("measurements.id", ondelete="SET NULL"), nullable=True)

    garment_style = Column(String(80), nullable=False) # e.g. "Bandhgala & Jodhpuri Trouser"
    fabric_name = Column(String(150), nullable=True) # e.g. "Raymond Super 120s Charcoal"
    fabric_mill = Column(String(100), nullable=True) # e.g. "Raymond Savile Collection India"
    fabric_width_in = Column(Float, default=58.0, nullable=False)
    fabric_pattern = Column(String(30), default="plain", nullable=False)
    fabric_image_url = Column(String(255), nullable=True)

    # Calculated metrics
    total_meters = Column(Float, nullable=False)
    total_yards = Column(Float, nullable=False)
    total_gaj = Column(Float, nullable=False)
    jacket_meters = Column(Float, default=0.0)
    trouser_meters = Column(Float, default=0.0)
    lining_meters = Column(Float, default=0.0)
    canvas_meters = Column(Float, default=0.0)

    # Commercials
    fabric_cost = Column(Float, default=0.0)
    stitching_cost = Column(Float, default=0.0)
    total_bill = Column(Float, default=0.0)
    advance_paid = Column(Float, default=0.0)
    balance_amount = Column(Float, default=0.0)

    # Workshop tracking
    status = Column(String(40), default="Trial Scheduled", nullable=False, index=True)
    trial_stage = Column(String(30), default="Trial #1")
    trial_date = Column(String(40), nullable=True)
    delivery_date = Column(String(40), nullable=True)
    senior_cutter = Column(String(100), default="Master V. Sharma")
    workshop_section = Column(String(100), default="Marine Lines Workshop")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    measurement = relationship("Measurement", back_populates="orders")

    def to_dict(self):
        return {
            "id": self.id,
            "order_no": self.order_no,
            "customer_id": self.customer_id,
            "customer_name": self.customer.name if self.customer else "Unknown",
            "customer_phone": self.customer.phone if self.customer else "",
            "measurement_id": self.measurement_id,
            "garment_style": self.garment_style,
            "fabric_name": self.fabric_name or "Standard Wool Suiting",
            "fabric_mill": self.fabric_mill or "Bespoke Mill",
            "fabric_width_in": self.fabric_width_in,
            "fabric_pattern": self.fabric_pattern,
            "fabric_image_url": self.fabric_image_url or "",
            "total_meters": self.total_meters,
            "total_yards": self.total_yards,
            "total_gaj": self.total_gaj,
            "jacket_meters": self.jacket_meters,
            "trouser_meters": self.trouser_meters,
            "lining_meters": self.lining_meters,
            "canvas_meters": self.canvas_meters,
            "fabric_cost": self.fabric_cost,
            "stitching_cost": self.stitching_cost,
            "total_bill": self.total_bill,
            "advance_paid": self.advance_paid,
            "balance_amount": self.balance_amount,
            "status": self.status,
            "trial_stage": self.trial_stage,
            "trial_date": self.trial_date or "To be scheduled",
            "delivery_date": self.delivery_date or "To be determined",
            "senior_cutter": self.senior_cutter,
            "workshop_section": self.workshop_section,
            "notes": self.notes or "",
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

