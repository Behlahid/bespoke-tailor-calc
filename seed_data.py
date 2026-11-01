"""
Seed Script to populate initial demo atelier data matching the Stitch design system.
"""

from database import engine, SessionLocal, init_db
from models import Customer, Measurement, Order
from calculator import TailorYardageCalculator

def seed():
    init_db()
    db = SessionLocal()

    # Avoid duplicate seeding
    if db.query(Customer).first():
        print("Database already contains data, skipping seed.")
        db.close()
        return

    print("Seeding Atelier Customer & Measurement Ledger...")

    # Customer 1: Vikram Singhania
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
        neck=16.5,
        shoulder=18.2,
        chest=41.5,
        bicep=14.0,
        wrist=7.5,
        waist=34.0,
        hip=40.0,
        inseam=32.5,
        outseam=41.0,
        thigh=24.5,
        calf=15.5,
        jacket_length=30.0,
        shirt_length=29.5,
        sleeve_length=25.0,
        ease_preset="barabar",
        posture_notes="Right shoulder drop -0.5 inch. Erect stance, hollow lower back."
    )
    db.add(m1)
    db.flush()

    # Calculate exact yardage for Vikram's Bandhgala & Trouser
    calc1 = TailorYardageCalculator.calculate(
        garment_style="bandhgala",
        measurements={"chest": 41.5, "waist": 34.0, "hip": 40.0, "jacket_length": 30.0, "sleeve_length": 25.0, "outseam": 41.0},
        fabric_width_inches=58.0,
        pattern_type="plain",
        fit_preset="barabar"
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
        fabric_image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuB_bL4kRLj8RrawKBarfJam2KKAgs2U4c1rTl9eiAooSEox4iy9OyCml_jiUrW4oiozWRUK95ZVEYkLjmgG-pbfHej7AigLBdo9Zf5x_uiaZAqF3kCUpyqbBQ0cWwOhpV-wfXtJCTTYyaPNoXgNa2xlIiZw6U8cpEw0ZSRR6u6Pc_YNgRBxkIZTRt-bGPaHIjAcRsquRvzBjDnDCTDstSB6N9K-CwHWobamucVslg",
        total_meters=calc1["total_meters"], # 3.45m
        total_yards=calc1["total_yards"],
        total_gaj=calc1["total_gaj"],
        jacket_meters=calc1["breakdown"]["jacket_meters"],
        trouser_meters=calc1["breakdown"]["trouser_meters"],
        lining_meters=calc1["breakdown"]["lining_meters"],
        canvas_meters=calc1["breakdown"]["canvas_meters"],
        fabric_cost=8452.50,
        stitching_cost=6500.00,
        total_bill=16935.00,
        advance_paid=10000.00,
        balance_amount=6935.00,
        status="Trial Scheduled",
        trial_stage="Trial #2",
        trial_date="Kal Subah 11:30 AM (12 Nov 2024)",
        delivery_date="18 Nov 2024",
        senior_cutter="Master V. Sharma",
        workshop_section="Marine Lines Section",
        notes="Basting stitch applied on chest and armscye. Thaan cut and assigned to Karigar Karim."
    )
    db.add(o1)

    # Customer 2: Rajesh Mehra
    c2 = Customer(
        name="Rajesh Mehra",
        phone="+91 98190 22341",
        email="rajesh.mehra@heritageholdings.com",
        city="South Mumbai",
        notes="Preferences: Classic double pleats on trouser, 1.75 inch turn-up cuffs."
    )
    db.add(c2)
    db.flush()

    m2 = Measurement(
        customer_id=c2.id,
        unit="in",
        neck=17.0,
        shoulder=18.5,
        chest=43.0,
        bicep=14.5,
        wrist=7.75,
        waist=36.0,
        hip=42.0,
        inseam=31.5,
        outseam=40.5,
        thigh=25.0,
        calf=16.0,
        jacket_length=30.5,
        shirt_length=30.0,
        sleeve_length=25.5,
        ease_preset="barabar",
        posture_notes="Normal posture with slight corpulence."
    )
    db.add(m2)
    db.flush()

    calc2 = TailorYardageCalculator.calculate(
        garment_style="suit_2pc",
        measurements={"chest": 43.0, "waist": 36.0, "hip": 42.0, "jacket_length": 30.5, "sleeve_length": 25.5, "outseam": 40.5},
        fabric_width_inches=58.0,
        pattern_type="stripe",
        fit_preset="barabar",
        extra_options={"cuffs": True, "pleats": True}
    )

    o2 = Order(
        order_no="BY-2024-90",
        customer_id=c2.id,
        measurement_id=m2.id,
        garment_style="2-Piece Bespoke Lounge Suit",
        fabric_name="Scabal Super 140s Navy Pinstripe",
        fabric_mill="Scabal Savile Row",
        fabric_width_in=58.0,
        fabric_pattern="stripe",
        fabric_image_url="https://lh3.googleusercontent.com/aida-public/AB6AXuCW6Bu7RfU93Ck8Udy5QtwdKzpB7_VUS_2xJPcHCCXyPz8rEvJMNOqBREr7J3cQ2hDFpBzVaD7bMo0LhYJjpyTyiKAoVBCQoso6kfIcCwYr8w9tmbcG68_vT1td03Dgp_i2Ke7Eykvo0WaFK7eXNcljWs3la81W-iTTrTxUXLZ7-MnBZCv1XqtjA3GOFY4Mcrlekmw4WxIVcN6vVRnUBuS0hWL8ARuTyE6PvMoTgw",
        total_meters=calc2["total_meters"],
        total_yards=calc2["total_yards"],
        total_gaj=calc2["total_gaj"],
        jacket_meters=calc2["breakdown"]["jacket_meters"],
        trouser_meters=calc2["breakdown"]["trouser_meters"],
        lining_meters=calc2["breakdown"]["lining_meters"],
        canvas_meters=calc2["breakdown"]["canvas_meters"],
        fabric_cost=14200.00,
        stitching_cost=8500.00,
        total_bill=22700.00,
        advance_paid=15000.00,
        balance_amount=7700.00,
        status="Cutting",
        trial_stage="Basting",
        trial_date="15 Nov 2024 (Thursday)",
        delivery_date="22 Nov 2024",
        senior_cutter="Master V. Sharma",
        workshop_section="Kalbadevi Section",
        notes="Stripes must align across front pocket flaps and chest welt."
    )
    db.add(o2)

    # Customer 3: Amit Shah
    c3 = Customer(
        name="Amit Shah",
        phone="+91 97690 88123",
        email="amit.shah@gujaratimotors.com",
        city="Mumbai (Dadar)",
        notes="Prefers relaxed dhila fit for ceremonial wear."
    )
    db.add(c3)
    db.flush()

    m3 = Measurement(
        customer_id=c3.id,
        unit="in",
        neck=16.0,
        shoulder=17.5,
        chest=39.0,
        bicep=13.5,
        wrist=7.25,
        waist=33.0,
        hip=38.5,
        inseam=31.0,
        outseam=40.0,
        thigh=23.5,
        calf=15.0,
        jacket_length=28.0,
        shirt_length=42.0,
        sleeve_length=24.5,
        ease_preset="dhila",
        posture_notes="Square shoulders, standard erect carriage."
    )
    db.add(m3)
    db.flush()

    calc3 = TailorYardageCalculator.calculate(
        garment_style="kurta_pajama",
        measurements={"chest": 39.0, "waist": 33.0, "hip": 38.5, "shirt_length": 42.0, "sleeve_length": 24.5, "outseam": 40.0},
        fabric_width_inches=44.0, # Standard cotton width
        pattern_type="plain",
        fit_preset="dhila"
    )

    o3 = Order(
        order_no="BY-2024-91",
        customer_id=c3.id,
        measurement_id=m3.id,
        garment_style="Raw Silk Kurta & Aligarhi Pajama",
        fabric_name="Bhagalpur Mulberry Silk Cream (44\" Width)",
        fabric_mill="Khadi & Silk Emporium",
        fabric_width_in=44.0,
        fabric_pattern="plain",
        total_meters=calc3["total_meters"],
        total_yards=calc3["total_yards"],
        total_gaj=calc3["total_gaj"],
        jacket_meters=0.0,
        trouser_meters=calc3["total_meters"],
        lining_meters=0.0,
        canvas_meters=0.0,
        fabric_cost=4200.00,
        stitching_cost=2800.00,
        total_bill=7000.00,
        advance_paid=7000.00,
        balance_amount=0.00,
        status="Ready for Delivery",
        trial_stage="Final Completed",
        trial_date="Completed",
        delivery_date="Today 4:00 PM",
        senior_cutter="Master Karim",
        workshop_section="Dadar Workshop",
        notes="Silk buttons hand-rolled, side slits reinforced."
    )
    db.add(o3)

    db.commit()
    db.close()
    print("Seed data successfully committed to database!")

if __name__ == "__main__":
    seed()
