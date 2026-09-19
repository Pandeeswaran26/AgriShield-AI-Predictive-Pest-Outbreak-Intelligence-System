"""
Agronomic Growth Stage Engine for AgriShield AI.

Calculates Days After Planting (DAP), current physiological growth stage,
stage progress %, water demand intensity, and nutrient demand profile
based on crop-specific biological timelines.
"""

from datetime import date, datetime
from typing import Dict, Any, Optional, List, Tuple


# Crop Growth Stage Durations in Days After Planting (DAP)
# Format: (stage_name, start_day, end_day, water_demand, nitrogen_demand, potassium_demand, description)
CROP_GROWTH_SCHEDULES: Dict[str, List[Tuple[str, int, int, str, str, str, str]]] = {
    "Rice": [
        ("Germination & Nursery", 0, 15, "Low", "Low", "Low", "Seed emergence and nursery seedling establishment."),
        ("Transplanting & Recovery", 16, 25, "High", "Medium", "Medium", "Root anchoring in puddled field; shallow standing water required."),
        ("Tillering", 26, 50, "High", "High", "Medium", "Active vegetative shoot multiplication; critical phase for nitrogen split."),
        ("Panicle Initiation & Stem Elongation", 51, 75, "Very High", "High", "High", "Rapid elongation; reproductive organs differentiating."),
        ("Flowering & Anthesis", 76, 95, "Very High", "Low", "High", "Pollination and spikelet fertilization; sensitive to moisture stress."),
        ("Milking & Dough (Grain Filling)", 96, 120, "Medium", "Low", "Medium", "Carbohydrate translocation into grains; gradual water drainage."),
        ("Maturity & Harvest", 121, 140, "Low", "None", "None", "Grains turn golden yellow; field completely drained 7-10 days before harvest."),
    ],
    "Cotton": [
        ("Germination & Emergence", 0, 12, "Low", "Low", "Low", "Cotyledon emergence and primary taproot growth."),
        ("Seedling & Early Vegetative", 13, 35, "Medium", "Medium", "Low", "True leaf development and monopodial branch formation."),
        ("Squaring (Bud Formation)", 36, 60, "High", "High", "Medium", "Floral bud (square) initiation; highly susceptible to bollworm moths."),
        ("Flowering & Boll Setting", 61, 105, "Very High", "High", "High", "Peak water and potassium requirement; white/pink flower development."),
        ("Boll Development & Maturation", 106, 140, "Medium", "Low", "High", "Boll enlargement and fiber elongation; watch for sucking pests."),
        ("Boll Bursting & Defoliation", 141, 170, "Low", "None", "None", "Bolls opening revealing white lint; dry sunny weather preferred."),
        ("Maturity & Harvest", 171, 195, "Low", "None", "None", "Final lint picking; immediate crop residue destruction recommended."),
    ],
    "Tomato": [
        ("Nursery & Seedling", 0, 25, "Low", "Low", "Low", "Germination and seedling establishment in trays or nursery beds."),
        ("Vegetative Establishment", 26, 45, "Medium", "High", "Medium", "Rapid root system and foliage expansion post-transplanting."),
        ("Flowering & Fruit Set", 46, 70, "High", "High", "High", "Yellow flower clusters and early berry formation; sensitive to blossom end rot."),
        ("Fruit Development & Enlargement", 71, 95, "Very High", "Medium", "High", "Rapid green fruit expansion; consistent soil moisture prevents cracking."),
        ("Ripening & Harvesting", 96, 130, "Medium", "Low", "Medium", "Color turning from breaker to red ripe; multiple picking cycles."),
    ],
    "Potato": [
        ("Sprout Development", 0, 15, "Low", "Low", "Low", "Eyes germinate and develop sprouts beneath soil surface."),
        ("Vegetative Canopy Growth", 16, 35, "Medium", "High", "Medium", "Leaves and stems emerge above ground; start of stolon initiation."),
        ("Tuber Initiation", 36, 55, "High", "High", "High", "Stolon tips swell to form miniature tubers; hill soil around base."),
        ("Tuber Bulking", 56, 90, "Very High", "Medium", "Very High", "Tubers accumulate starch rapidly; peak water and potassium consumption."),
        ("Maturation & Skin Setting", 91, 115, "Low", "None", "None", "Canopy senesces and vines yellow; haulm cutting 10 days before digging."),
    ],
    "Corn": [
        ("Emergence (VE-V2)", 0, 14, "Low", "Low", "Low", "Sprout breaks through soil surface; root system establishes."),
        ("Rapid Vegetative (V3-V10)", 15, 45, "High", "High", "Medium", "Rapid whorl leaf growth and nodal root development."),
        ("Tasseling & Silking (VT-R1)", 46, 65, "Very High", "High", "High", "Pollen shed and ear silk emergence; critical water stress window."),
        ("Grain Filling & Dough (R2-R4)", 66, 95, "High", "Medium", "High", "Kernel starch accumulation and ear development."),
        ("Physiological Maturity & Drydown (R5-R6)", 96, 120, "Low", "None", "None", "Black layer formation; dry down for harvest."),
    ],
    "Wheat": [
        ("Germination & Crown Root", 0, 20, "Low", "Medium", "Low", "Seed emergence and crown root initiation."),
        ("Tillering & Jointing", 21, 55, "High", "High", "Medium", "Stem elongation and active secondary shoot tillering."),
        ("Booting & Heading", 56, 75, "Very High", "High", "High", "Ear emergence from flag leaf sheath."),
        ("Flowering & Anthesis", 76, 90, "Very High", "Low", "High", "Spikelet pollination; avoid hot dry winds."),
        ("Grain Filling (Milking to Dough)", 91, 115, "Medium", "Low", "Medium", "Kernel swelling and starch deposition."),
        ("Maturity & Ripening", 116, 130, "Low", "None", "None", "Straw turns golden brown; grain moisture drops below 14%."),
    ],
    "Apple": [
        ("Dormancy & Silver Tip", 0, 30, "Low", "Low", "Low", "Buds dormant to early silver tip emergence."),
        ("Green Tip & Tight Cluster", 31, 55, "Medium", "Medium", "Medium", "Leaves unfurling; high susceptibility to Apple Scab."),
        ("Pink Bud & Full Bloom", 56, 75, "High", "Low", "High", "Pollination period; avoid broad-spectrum insecticide sprays."),
        ("Petal Fall & Fruit Set", 76, 100, "High", "High", "High", "Young fruitlet development and thinning window."),
        ("Fruit Growth & Sizing", 101, 160, "High", "Medium", "High", "Rapid apple sizing and color development."),
        ("Harvest Maturity", 161, 190, "Low", "None", "Low", "Starch converts to sugar; picking window."),
    ],
    "Grape": [
        ("Budbreak & Shoot Emergence", 0, 30, "Low", "Medium", "Low", "New shoots emerge from winter buds."),
        ("Rapid Shoot Growth", 31, 55, "Medium", "High", "Medium", "Canopy development and inflorescence appearance."),
        ("Flowering & Bloom", 56, 75, "Medium", "Low", "Medium", "Cap fall and fertilization; avoid moisture on clusters."),
        ("Berry Set & Pea Size", 76, 105, "High", "Medium", "High", "Berry cell division; susceptible to Powdery Mildew and Black Rot."),
        ("Veraison (Color Change & Softening)", 106, 135, "Medium", "Low", "High", "Sugar accumulation and acid decline."),
        ("Harvest Maturity", 136, 160, "Low", "None", "None", "Brix levels reach target for wine or table grapes."),
    ],
}


def normalize_crop_name(crop: str) -> str:
    """Matches any crop string to supported schedule keys."""
    if not crop:
        return "Rice"
    c_lower = crop.lower().strip()
    for key in CROP_GROWTH_SCHEDULES.keys():
        if key.lower() in c_lower or c_lower in key.lower():
            return key
    if "paddy" in c_lower or "rice" in c_lower:
        return "Rice"
    if "cotton" in c_lower or "kapas" in c_lower:
        return "Cotton"
    if "maize" in c_lower or "corn" in c_lower:
        return "Corn"
    if "tuber" in c_lower or "potato" in c_lower:
        return "Potato"
    return "Rice"


def calculate_growth_stage(
    planting_date_str: Optional[str],
    crop_name: str,
    target_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Calculates Days After Planting (DAP) and determines the physiological growth stage.

    Returns:
    {
        "days_after_planting": int,
        "growth_stage": str,
        "stage_description": str,
        "water_demand": str ("Low"|"Medium"|"High"|"Very High"),
        "nitrogen_demand": str ("None"|"Low"|"Medium"|"High"),
        "potassium_demand": str ("None"|"Low"|"Medium"|"High"|"Very High"),
        "is_estimated": bool,
        "all_stages": list,
        "progress_percent": float,
        "data_source": "CALCULATED (ESTIMATE)"
    }
    """
    normalized_crop = normalize_crop_name(crop_name)
    schedule = CROP_GROWTH_SCHEDULES.get(normalized_crop, CROP_GROWTH_SCHEDULES["Rice"])

    ref_date = target_date or date.today()

    dap = 30  # default fallback if planting_date is missing
    is_estimated = True

    if planting_date_str:
        try:
            # Handle ISO string YYYY-MM-DD
            clean_date = planting_date_str.split("T")[0].strip()
            p_date = datetime.strptime(clean_date, "%Y-%m-%d").date()
            diff_days = (ref_date - p_date).days
            dap = max(0, diff_days)
            is_estimated = False
        except Exception:
            dap = 30
            is_estimated = True

    # Find matching stage from schedule
    current_stage = schedule[-1]  # fallback to last stage if DAP exceeds
    for stage_tuple in schedule:
        name, start_d, end_d, w_dem, n_dem, k_dem, desc = stage_tuple
        if start_d <= dap <= end_d:
            current_stage = stage_tuple
            break

    total_cycle_days = schedule[-1][2] or 140
    progress_pct = min(100.0, round((dap / total_cycle_days) * 100.0, 1))

    return {
        "days_after_planting": dap,
        "growth_stage": current_stage[0],
        "stage_description": current_stage[6],
        "water_demand": current_stage[3],
        "nitrogen_demand": current_stage[4],
        "potassium_demand": current_stage[5],
        "crop": normalized_crop,
        "is_estimated": is_estimated,
        "progress_percent": progress_pct,
        "total_crop_cycle_days": total_cycle_days,
        "data_source": "CALCULATED (ESTIMATE)",
        "all_stages": [
            {
                "name": s[0],
                "start_day": s[1],
                "end_day": s[2],
                "water_demand": s[3],
                "nitrogen_demand": s[4],
                "potassium_demand": s[5],
                "description": s[6],
                "is_current": s[0] == current_stage[0],
            }
            for s in schedule
        ],
    }
