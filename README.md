# Bombay Master Tailors — Bespoke Measurement & Fabric-Yardage Calculator

> **The Unbuilt Problem Solved**: Replaces traditional tailor paper diaries (*khata*) and guesswork fabric estimates with an interactive anatomical SVG caliper diagram, Python mathematical yardage calculation engine, and full MySQL customer docket management.

---

## 🌟 Key Features

1. **Interactive SVG Mannequin Measurement Capture (`Naap`)**:
   - Touch/click body parts on an anatomical blueprint mannequin (Neck, Shoulder, Chest, Bicep, Wrist, Waist, Hip, Inseam, Outseam, Thigh, Calf, Lengths).
   - Angle switcher: **FRONT**, **PROFILE**, and **LOWER** views.
   - Live basting contour highlights active target.
   - Workshop tactile stepper controls (`±0.25"`, `±0.50"`).
   - Instant unit conversion between **Inches (इंच)** and **Centimeters (सेमी)**.
   - Masterji ease presets: *Chust (Slim Fit +1.5")*, *Barabar (Regular Fit +2.5")*, *Dhila/Khula (Relaxed Fit +4.0")*.
   - Posture observation recording (*Jhuka hua kandha, prominent abdomen, erect stance*).

2. **Python Fabric-Yardage Engine (`Kapda`) with 3D Drape Simulator**:
   - Exact mathematical calculation of cloth needed based on garment architecture and cloth width (Pana/Arz: 36", 44", 54", 58"-60" Bada Pana).
   - Garment support: Bandhgala & Jodhpuri, 2-Piece Suit, 3-Piece Savile Suit, Royal Sherwani, Kurta Pajama, Bespoke Shirt, Waistcoat/Sadri.
   - Pattern match buffers: Plain (0%), Directional/Velvet/Nap (+12%), Pinstripes (+10%), Windowpane/Plaids (+20%).
   - Metrics in **Meters**, **Gaj (Gaz)**, and **Yards**.
   - Sub-component breakdown: Jacket cloth, Trouser cloth, Lining (*Astar*), and Horsehair Canvas (*Bukram*).
   - **3D Three.js WebGL Drape Simulator**: Real-time wave physics simulating cloth fall over a tailor's dress form with interactive mouse/touch rotation and fabric stiffness selection (Tweed, Super 120s, Silk).

3. **Client Fitting Ledger & Customer Diary (`Khata`)**:
   - Complete record of commissions, trial schedules, and delivery dates.
   - Real-time atelier KPIs (Active orders, total fabric cut, fabric inventory value in ₹, urgent trials this week).
   - Instant search & status filtering (*Sabhi, Trial Baaki, Ready for Delivery, Advance Baaki*).

4. **Order Spec Sheet & Cutting Docket (`Parchi`)**:
   - Savile Row & Bombay Master Tailors printable cutting ticket (*Katai Parchi*).
   - Itemized cloth and karigari labour billing.
   - 1-click browser printing (`window.print()`) with print-optimized CSS and WhatsApp docket sharing.

---

## 🚀 Quick Start

### 1. Activate Environment & Run
```powershell
cd C:\Users\Behlah\.gemini\antigravity\scratch\bespoke-tailor-calc
.\.venv\Scripts\activate
python main.py
```
Open **[http://localhost:8000](http://localhost:8000)** in your browser!

### 2. MySQL Configuration (Production)
The system connects to MySQL via `DATABASE_URL`:
```bash
set DATABASE_URL=mysql+pymysql://<user>:<password>@localhost:3306/bespoke_tailordb
```
*(If MySQL is not currently running, the app automatically and smoothly defaults to SQLite `./bespoke_tailor.db` with zero configuration needed!)*

To run the raw MySQL schema:
```bash
mysql -u root -p < schema.sql
```

