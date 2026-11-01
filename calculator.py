"""
Bespoke Tailoring Yardage & Cutting Calculation Engine
Implements traditional Savile Row and Bombay Master Tailor yardage formulas,
accounting for cloth width (Pana/Arz), pattern repeat matching, garment styling,
anatomical measurements, ease allowances, and cutting layout optimization.
"""

from typing import Dict, Any, Optional

# Standard conversion constants
INCH_TO_METER = 0.0254
METER_TO_INCH = 39.3700787
METER_TO_YARD = 1.0936133
YARD_TO_METER = 0.9144
# In traditional Indian tailoring, 1 Gaj (Gaz) is legally and commercially equivalent to 1 Yard (36 inches) = 0.9144m
METER_TO_GAJ = 1.0936133

# Pattern repeat buffer percentages
PATTERN_REPEAT_BUFFERS = {
    "plain": 0.0,            # Solid cloth: 0% extra
    "directional": 0.12,     # Velvet, corduroy, wool nap (Rukh): +12%
    "stripe": 0.10,          # Vertical / horizontal pinstripes: +10%
    "plaid": 0.20,           # Tartans, Glenurquhart checks, Windowpane: +20%
}

# Ease allowances in inches on circumference
EASE_PRESETS = {
    "chust": {"chest": 1.5, "waist": 1.0, "hip": 1.5, "bicep": 1.0, "label": "Chust (Slim Fit)"},
    "barabar": {"chest": 2.5, "waist": 2.0, "hip": 2.5, "bicep": 1.75, "label": "Barabar (Regular Fit)"},
    "dhila": {"chest": 4.0, "waist": 3.5, "hip": 4.0, "bicep": 2.5, "label": "Dhila / Khula (Relaxed Fit)"},
}

class TailorYardageCalculator:
    """
    Precision cutter calculation engine for bespoke garments.
    """

    @staticmethod
    def calculate(
        garment_style: str,
        measurements: Dict[str, float],
        fabric_width_inches: float = 58.0,
        pattern_type: str = "plain",
        fit_preset: str = "barabar",
        extra_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate precise yardage requirements.
        All input measurements in `measurements` should be in INCHES.
        """
        extra_options = extra_options or {}

        # Default fallbacks if certain measurements are omitted
        chest = float(measurements.get("chest", 41.5))
        waist = float(measurements.get("waist", 34.0))
        hip = float(measurements.get("hip", 40.0))
        shoulder = float(measurements.get("shoulder", 18.2))
        sleeve_length = float(measurements.get("sleeve_length", 25.0))
        jacket_length = float(measurements.get("jacket_length", 30.0))
        trouser_outseam = float(measurements.get("outseam", 41.0))
        trouser_inseam = float(measurements.get("inseam", 32.5))
        shirt_length = float(measurements.get("shirt_length", 29.5))
        waistcoat_length = float(measurements.get("waistcoat_length", 24.0))

        # Ease preset
        ease = EASE_PRESETS.get(fit_preset, EASE_PRESETS["barabar"])

        # Breakdown variables in inches
        jacket_cloth_in = 0.0
        trouser_cloth_in = 0.0
        waistcoat_cloth_in = 0.0
        shirt_cloth_in = 0.0
        lining_in = 0.0
        canvas_in = 0.0
        pocketing_in = 0.0

        is_double_width = fabric_width_inches >= 54.0
        is_medium_width = 42.0 <= fabric_width_inches < 54.0
        is_single_width = fabric_width_inches < 42.0

        raw_style = garment_style.lower().strip().replace("-", "_").replace(" ", "_")

        # Determine sub-components needed
        needs_jacket = False
        needs_trouser = False
        needs_waistcoat = False
        needs_shirt = False
        needs_kurta = False
        needs_pajama = False
        is_sherwani = False

        if any(k in raw_style for k in ["bandhgala", "jodhpuri_suit"]):
            needs_jacket = True
            # By default Bandhgala in atelier context includes Jodhpuri trousers unless specified
            if not extra_options.get("jacket_only", False):
                needs_trouser = True
        elif any(k in raw_style for k in ["suit_3pc", "three_piece"]):
            needs_jacket = True
            needs_trouser = True
            needs_waistcoat = True
        elif any(k in raw_style for k in ["suit_2pc", "suit", "two_piece", "tuxedo"]):
            needs_jacket = True
            needs_trouser = True
        elif any(k in raw_style for k in ["blazer", "sports_coat", "jacket"]):
            needs_jacket = True
        elif any(k in raw_style for k in ["trouser", "pant", "jodhpuri"]):
            needs_trouser = True
        elif any(k in raw_style for k in ["waistcoat", "sadri", "nehru"]):
            needs_waistcoat = True
        elif any(k in raw_style for k in ["kurta_pajama", "kurta_salwar"]):
            needs_kurta = True
            needs_pajama = True
        elif any(k in raw_style for k in ["kurta"]):
            needs_kurta = True
        elif any(k in raw_style for k in ["sherwani", "achkan"]):
            needs_jacket = True
            is_sherwani = True
            needs_trouser = True
        elif any(k in raw_style for k in ["shirt"]):
            needs_shirt = True
        else:
            # Fallback: full 2pc suit
            needs_jacket = True
            needs_trouser = True

        # ==================== 1. JACKET / COAT / BANDHGALA ====================
        if needs_jacket:
            eff_jacket_len = jacket_length if not is_sherwani else max(jacket_length, 42.0)
            jacket_hem = 2.5
            facing_buffer = 6.0
            sleeve_hem = 2.0

            if is_double_width:
                # 58"-60" Suiting: Front panels and back body nest side-by-side
                body_len = eff_jacket_len + jacket_hem + facing_buffer
                sleeve_len = sleeve_length + sleeve_hem
                
                # Large chest penalty (>46") or corpulent stance: require stagger
                stout_penalty = 7.0 if chest > 46.0 else 0.0
                db_penalty = 8.0 if extra_options.get("double_breasted", False) else 0.0

                jacket_cloth_in = body_len + sleeve_len + stout_penalty + db_penalty
            elif is_medium_width: # 44-45"
                jacket_cloth_in = (2 * eff_jacket_len) + sleeve_length + 12.0
            else: # 36" Single Width
                jacket_cloth_in = (2 * eff_jacket_len) + (2 * sleeve_length) + 16.0

            lining_in += (eff_jacket_len + 3.0) + (sleeve_length + 2.0)
            canvas_in += (eff_jacket_len + 6.0)

        # ==================== 2. TROUSERS / JODHPURI ====================
        if needs_trouser:
            turnup_cuff = 3.5 if extra_options.get("cuffs", False) else 0.0
            pleats_buffer = 2.0 if extra_options.get("pleats", True) else 0.0
            trouser_hem_waistband = 5.5 + turnup_cuff + pleats_buffer

            if is_double_width:
                # In 58" width, standard hip (<45") allows front and back legs to invert head-to-toe
                if hip <= 45.0:
                    trouser_cloth_in = trouser_outseam + trouser_hem_waistband
                else:
                    # Prominent seat requires staggered placement
                    trouser_cloth_in = trouser_outseam + trouser_hem_waistband + 9.0
            else:
                # 36" or 44": each leg must be cut sequentially
                trouser_cloth_in = (2 * trouser_outseam) + trouser_hem_waistband + 4.0

            pocketing_in += 14.0

        # ==================== 3. WAISTCOAT / NEHRU ====================
        if needs_waistcoat:
            is_nehru = any(k in raw_style for k in ["sadri", "nehru"])
            wc_len = waistcoat_length if not is_nehru else max(waistcoat_length, 27.0)

            if is_double_width:
                if is_nehru:
                    waistcoat_cloth_in = wc_len + 8.0
                else:
                    waistcoat_cloth_in = wc_len + 4.0
                    lining_in += (wc_len + 3.0)
            else:
                waistcoat_cloth_in = (2 * wc_len) + 6.0
                if not is_nehru:
                    lining_in += (wc_len + 3.0)

        # ==================== 4. SHIRT ====================
        if needs_shirt:
            if is_double_width:
                shirt_cloth_in = shirt_length + sleeve_length + 8.0
            else:
                shirt_cloth_in = (2 * shirt_length) + sleeve_length + 10.0

        # ==================== 5. KURTA & PAJAMA ====================
        if needs_kurta:
            k_len = max(shirt_length, 41.0)
            if is_double_width:
                k_cloth = k_len + sleeve_length + 8.0
            else:
                k_cloth = (2 * k_len) + sleeve_length + 8.0
            shirt_cloth_in += k_cloth

        if needs_pajama:
            if is_double_width:
                p_cloth = trouser_outseam + 12.0
            else:
                p_cloth = (2 * trouser_outseam) + 10.0
            shirt_cloth_in += p_cloth

        # Total base cloth in inches
        base_cloth_in = jacket_cloth_in + trouser_cloth_in + waistcoat_cloth_in + shirt_cloth_in

        # Pattern Repeat Buffer
        pattern_rate = PATTERN_REPEAT_BUFFERS.get(pattern_type.lower(), 0.0)
        pattern_buffer_in = base_cloth_in * pattern_rate
        total_cloth_in = base_cloth_in + pattern_buffer_in

        # Convert to Meters, Yards, Gaj
        total_meters = round(total_cloth_in * INCH_TO_METER, 2)
        total_yards = round(total_cloth_in / 36.0, 2)
        total_gaj = round(total_meters * METER_TO_GAJ, 2)

        jacket_meters = round(jacket_cloth_in * INCH_TO_METER, 2)
        trouser_meters = round(trouser_cloth_in * INCH_TO_METER, 2)
        waistcoat_meters = round(waistcoat_cloth_in * INCH_TO_METER, 2)
        buffer_meters = round(pattern_buffer_in * INCH_TO_METER, 2)
        lining_meters = round(lining_in * INCH_TO_METER, 2)
        canvas_meters = round(canvas_in * INCH_TO_METER, 2)

        # Efficiency calculation
        est_efficiency = 92 if is_double_width else 83
        if pattern_type.lower() != "plain":
            est_efficiency -= 4

        # Lay recommendation description
        if is_double_width:
            lay_strategy = (
                f"Double Width ({int(fabric_width_inches)}\" Bada Panna): Inverted balance lay. "
                f"Front and back body panels nest side-by-side along grain. "
                f"Trouser legs folded on center crease."
            )
        else:
            lay_strategy = (
                f"Single/Medium Width ({int(fabric_width_inches)}\" Chhota/Standard Pana): Two-way staggered cut. "
                f"Each trouser leg and body section requires sequential lengthwise cutting."
            )

        return {
            "garment_style": garment_style,
            "fabric_width_inches": fabric_width_inches,
            "pattern_type": pattern_type,
            "fit_preset": fit_preset,
            "total_meters": total_meters,
            "total_yards": total_yards,
            "total_gaj": total_gaj,
            "breakdown": {
                "jacket_meters": jacket_meters,
                "trouser_meters": trouser_meters,
                "waistcoat_meters": waistcoat_meters,
                "buffer_meters": buffer_meters,
                "lining_meters": lining_meters,
                "canvas_meters": canvas_meters,
            },
            "efficiency_percent": est_efficiency,
            "scrappage_meters": round(total_meters * ((100 - est_efficiency) / 100), 2),
            "cutting_advice": lay_strategy,
            "ease_details": ease,
        }
