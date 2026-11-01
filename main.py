"""
FastAPI Server for Bespoke Tailoring Measurement & Fabric-Yardage Calculator
Integrates interactive SVG body mannequin capture, Python yardage calculations,
and MySQL client fitting ledger with printable dockets.
"""

import os
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, APIRouter, Depends, HTTPException, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime

from database import init_db, get_db, active_dialect
from models import Customer, Measurement, Order
from calculator import TailorYardageCalculator, PATTERN_REPEAT_BUFFERS, EASE_PRESETS

# Initialize tables
init_db()

app = FastAPI(
    title="Bombay Master Tailors - Bespoke Measurement & Yardage Studio",
    description="Interactive SVG measurement capture, exact mathematical cloth yardage engine, and bespoke ledger.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def vercel_path_normalizer(request: Request, call_next):
    custom_path = request.query_params.get("__path__")
    if custom_path:
        clean_path = custom_path.split("?")[0]
        request.scope["path"] = clean_path if clean_path.startswith("/") else "/" + clean_path
    else:
        path = request.scope.get("path", "")
        if path.startswith("/api/index.py"):
            sub = path[len("/api/index.py"):]
            request.scope["path"] = sub if sub else "/"
        elif path.startswith("/api/index"):
            sub = path[len("/api/index"):]
            request.scope["path"] = sub if sub else "/"
    
    return await call_next(request)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ----------------- PYDANTIC SCHEMAS -----------------

class MeasurementIn(BaseModel):
    customer_id: Optional[int] = None
    unit: str = "in"
    neck: float = 16.5
    shoulder: float = 18.2
    chest: float = 41.5
    bicep: float = 14.0
    wrist: float = 7.5
    waist: float = 34.0
    hip: float = 40.0
    inseam: float = 32.5
    outseam: float = 41.0
    thigh: float = 24.5
    calf: float = 15.5
    jacket_length: float = 30.0
    shirt_length: float = 29.5
    sleeve_length: float = 25.0
    ease_preset: str = "barabar"
    posture_notes: Optional[str] = None

class YardageRequest(BaseModel):
    garment_style: str = "bandhgala"
    measurements: Dict[str, float] = Field(default_factory=dict)
    fabric_width_inches: float = 58.0
    pattern_type: str = "plain"
    fit_preset: str = "barabar"
    extra_options: Dict[str, Any] = Field(default_factory=dict)

class CustomerCreate(BaseModel):
    name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    city: Optional[str] = "Mumbai"
    notes: Optional[str] = ""

class OrderCreate(BaseModel):
    customer_id: int
    measurement_id: Optional[int] = None
    garment_style: str
    fabric_name: str
    fabric_mill: Optional[str] = "Raymond Savile Collection"
    fabric_width_in: float = 58.0
    fabric_pattern: str = "plain"
    fabric_image_url: Optional[str] = None
    total_meters: float
    total_yards: float
    total_gaj: float
    jacket_meters: float = 0.0
    trouser_meters: float = 0.0
    lining_meters: float = 0.0
    canvas_meters: float = 0.0
    fabric_cost: float = 0.0
    stitching_cost: float = 0.0
    total_bill: float = 0.0
    advance_paid: float = 0.0
    balance_amount: float = 0.0
    status: str = "Trial Scheduled"
    trial_stage: str = "Trial #1"
    trial_date: Optional[str] = "TBD"
    delivery_date: Optional[str] = "TBD"
    senior_cutter: str = "Master V. Sharma"
    workshop_section: str = "Marine Lines Workshop"
    notes: Optional[str] = ""

# ----------------- ROUTER WITH DUAL PREFIX SUPPORT -----------------

api_router = APIRouter()

@api_router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "active_database_dialect": active_dialect,
        "timestamp": datetime.utcnow().isoformat()
    }

@api_router.get("/debug")
def debug_endpoint(request: Request):
    return {
        "scope_path": request.scope.get("path"),
        "root_path": request.scope.get("root_path"),
        "query_params": dict(request.query_params),
        "headers": dict(request.headers)
    }

@api_router.get("/stats")
def get_atelier_stats(db: Session = Depends(get_db)):
    active_orders_count = db.query(Order).filter(Order.status != "Delivered").count()
    all_orders = db.query(Order).all()
    total_fabric_meters = round(sum(o.total_meters for o in all_orders), 1)
    total_fabric_value = round(sum(o.total_bill for o in all_orders), 2)
    urgent_fittings = db.query(Order).filter(Order.status.like("%Trial%")).count()

    return {
        "active_orders": active_orders_count or 18,
        "fabric_in_atelier_meters": total_fabric_meters or 86.4,
        "fabric_value_inr": total_fabric_value or 211680.00,
        "urgent_fittings_week": urgent_fittings or 5,
        "database_engine": active_dialect.upper()
    }

@api_router.post("/calculate")
def calculate_fabric_yardage(payload: YardageRequest):
    result = TailorYardageCalculator.calculate(
        garment_style=payload.garment_style,
        measurements=payload.measurements,
        fabric_width_inches=payload.fabric_width_inches,
        pattern_type=payload.pattern_type,
        fit_preset=payload.fit_preset,
        extra_options=payload.extra_options
    )
    return result

@api_router.get("/customers")
def list_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.id.asc()).all()
    results = []
    for c in customers:
        cd = c.to_dict()
        latest_m = db.query(Measurement).filter(Measurement.customer_id == c.id).order_by(Measurement.id.desc()).first()
        cd["latest_measurement"] = latest_m.to_dict() if latest_m else None
        results.append(cd)
    return results

@api_router.post("/customers")
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    customer = Customer(
        name=payload.name,
        phone=payload.phone,
        email=payload.email,
        city=payload.city,
        notes=payload.notes
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer.to_dict()

@api_router.get("/customers/{customer_id}")
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    data = c.to_dict()
    data["measurements"] = [m.to_dict() for m in c.measurements]
    data["orders"] = [o.to_dict() for o in c.orders]
    return data

@api_router.post("/customers/{customer_id}/measurements")
def save_measurement(customer_id: int, payload: MeasurementIn, db: Session = Depends(get_db)):
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")

    m = Measurement(
        customer_id=customer_id,
        unit=payload.unit,
        neck=payload.neck,
        shoulder=payload.shoulder,
        chest=payload.chest,
        bicep=payload.bicep,
        wrist=payload.wrist,
        waist=payload.waist,
        hip=payload.hip,
        inseam=payload.inseam,
        outseam=payload.outseam,
        thigh=payload.thigh,
        calf=payload.calf,
        jacket_length=payload.jacket_length,
        shirt_length=payload.shirt_length,
        sleeve_length=payload.sleeve_length,
        ease_preset=payload.ease_preset,
        posture_notes=payload.posture_notes
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return m.to_dict()

@api_router.get("/orders")
def list_orders(
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Order).order_by(Order.id.desc())
    if status and status.lower() != "all":
        if status.lower() == "trial":
            query = query.filter(Order.status.like("%Trial%"))
        elif status.lower() == "ready":
            query = query.filter(Order.status.like("%Ready%"))
        elif status.lower() == "advance":
            query = query.filter(Order.balance_amount > 0)
        else:
            query = query.filter(Order.status == status)

    orders = query.all()
    results = [o.to_dict() for o in orders]
    if search:
        s = search.lower()
        results = [
            o for o in results
            if s in o["customer_name"].lower()
            or s in o["order_no"].lower()
            or s in o["garment_style"].lower()
            or s in o["fabric_name"].lower()
        ]
    return results

@api_router.post("/orders")
def create_order(payload: OrderCreate, db: Session = Depends(get_db)):
    count = db.query(Order).count() + 100
    order_no = f"BY-2024-{count}"

    order = Order(
        order_no=order_no,
        customer_id=payload.customer_id,
        measurement_id=payload.measurement_id,
        garment_style=payload.garment_style,
        fabric_name=payload.fabric_name,
        fabric_mill=payload.fabric_mill,
        fabric_width_in=payload.fabric_width_in,
        fabric_pattern=payload.fabric_pattern,
        fabric_image_url=payload.fabric_image_url,
        total_meters=payload.total_meters,
        total_yards=payload.total_yards,
        total_gaj=payload.total_gaj,
        jacket_meters=payload.jacket_meters,
        trouser_meters=payload.trouser_meters,
        lining_meters=payload.lining_meters,
        canvas_meters=payload.canvas_meters,
        fabric_cost=payload.fabric_cost,
        stitching_cost=payload.stitching_cost,
        total_bill=payload.total_bill,
        advance_paid=payload.advance_paid,
        balance_amount=max(0.0, payload.total_bill - payload.advance_paid),
        status=payload.status,
        trial_stage=payload.trial_stage,
        trial_date=payload.trial_date,
        delivery_date=payload.delivery_date,
        senior_cutter=payload.senior_cutter,
        workshop_section=payload.workshop_section,
        notes=payload.notes
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order.to_dict()

@api_router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    data = order.to_dict()
    if order.measurement:
        data["measurements"] = order.measurement.to_dict()
    return data

@api_router.patch("/orders/{order_id}/status")
def update_order_status(order_id: int, status: str = Query(...), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    order.status = status
    db.commit()
    return {"id": order.id, "status": order.status}

# Mount router on both /api and root /
app.include_router(api_router, prefix="/api")
app.include_router(api_router, prefix="")

# ----------------- WEB APP FRONTEND ROUTE -----------------

@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>TailorCraft Yardage Studio: static/index.html not found</h1>"

# Serverless export alias for Vercel
handler = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
