import json
import re
from sqlalchemy.orm import Session

from history.models import PredictionHistory


def clean_pest_name(raw_name: str) -> str:
    clean = re.sub(r"\s*\(.*?\)", "", raw_name or "")
    clean = re.sub(r"([a-z])([A-Z])", r"\1 \2", clean)
    return clean.strip()


_PEST_RULES = {
    "aphid": {
        "display": "Aphids",
        "actions": ["Inspect undersides of leaves and young shoots for colonies", "Check for honeydew and sooty mold development"],
        "prevention": ["Avoid excessive nitrogenous fertilizers which promote succulent growth", "Conserve natural predators like ladybird beetles and syrphid flies"],
        "pesticides": ["Imidacloprid 17.8% SL @ 50-60 ml/acre in 200L water", "Acetamiprid 20% SP @ 40-50 g/acre"],
        "organic": ["Neem Oil (Azadirachtin 10,000 ppm) @ 2 ml/L water", "Verticillium lecanii @ 5 g/L spray", "5% Neem Seed Kernel Extract (NSKE)"],
        "yield_impact": {"Low": 4.0, "Medium": 10.0, "High": 18.0},
    },
    "bollworm": {
        "display": "Bollworms (American / Pink / Spotted)",
        "actions": ["Install sex pheromone traps @ 5 traps/acre for pest monitoring", "Hand-pick and destroy flared-up squares and dropped bolls", "Scout 20 plants across diagonals for egg/larval threshold"],
        "prevention": ["Deep summer ploughing to expose pupae to sun and birds", "Avoid staggered sowing and maintain crop synchronization", "Destroy crop residues promptly after final picking"],
        "pesticides": ["Chlorantraniliprole 18.5% SC @ 60 ml/acre", "Emamectin Benzoate 5% SG @ 80-100 g/acre", "Spinosad 45% SC @ 60-75 ml/acre"],
        "organic": ["Release Trichogramma egg parasitoids @ 60,000/acre weekly", "Bt (Bacillus thuringiensis) formulation @ 2 g/L", "Nuclear Polyhedrosis Virus (HaNPV) @ 100 LE/acre"],
        "yield_impact": {"Low": 6.0, "Medium": 16.0, "High": 32.0},
    },
    "stem borer": {
        "display": "Yellow Stem Borer",
        "actions": ["Clip seedling leaf tips before transplanting to remove egg masses", "Monitor field for 'Dead Hearts' in vegetative stage and 'White Ears' in reproductive stage", "Install pheromone traps @ 4-5 traps/acre"],
        "prevention": ["Maintain optimum 2-3 cm water level; drain water periodically", "Synchronize planting with neighboring farms", "Harvest crop at ground level to destroy larvae inside stubbles"],
        "pesticides": ["Chlorantraniliprole 0.4% GR @ 4 kg/acre (broadcast in standing water)", "Cartap Hydrochloride 50% SP @ 400 g/acre in 200L water", "Fipronil 5% SC @ 400 ml/acre"],
        "organic": ["Trichogramma japonicum egg parasitoid cards @ 40,000/acre", "Bacillus thuringiensis kurstaki @ 2.5 g/L spray", "Neem cake soil application @ 100 kg/acre"],
        "yield_impact": {"Low": 5.0, "Medium": 14.0, "High": 28.0},
    },
    "brownplanthopper": {
        "display": "Brown Planthopper (BPH)",
        "actions": ["Provide 30 cm alleyways (pathways) every 2-3 meters in rice fields to improve air flow and sunlight", "Drain standing water from field for 3-4 days to arrest hopper multiplier cycle", "Scout the base of hills near water line"],
        "prevention": ["Refrain from indiscriminate use of synthetic pyrethroids which cause pest resurgence", "Balance nitrogen application; avoid heavy single-dose top dressings", "Use BPH-tolerant varieties where available"],
        "pesticides": ["Pymetrozine 50% WDG @ 120 g/acre in 200L water", "Triflumuron or Dinotefuran 20% SG @ 80-100 g/acre", "Triflumezopyrim 10% SC @ 94 ml/acre"],
        "organic": ["Neem Oil (3000 ppm) @ 5 ml/L spray directed strictly at plant base", "Beauveria bassiana @ 5 g/L directed at stem base"],
        "yield_impact": {"Low": 8.0, "Medium": 20.0, "High": 45.0},
    },
    "leaffolder": {
        "display": "Rice Leaf Folder",
        "actions": ["Look for longitudinal leaf folds with translucent feeding patches", "Unroll damaged leaves to check for active green caterpillars", "Pass a coir rope across crop canopy early morning to dislodge larvae"],
        "prevention": ["Avoid excess nitrogen; split fertilizer into 3-4 equal doses", "Keep field bunds clean of grassy alternate host weeds", "Avoid unnecessary early-season broad-spectrum sprays"],
        "pesticides": ["Flubendiamide 39.35% SC @ 20 ml/acre in 200L water", "Chlorantraniliprole 18.5% SC @ 60 ml/acre", "Cartap Hydrochloride 50% SP @ 400 g/acre"],
        "organic": ["Release Trichogramma chilonis @ 40,000/acre at initial leaf damage", "Neem Seed Kernel Extract (NSKE 5%) @ 10 kg/200L/acre", "Spray Bacillus thuringiensis @ 2 g/L"],
        "yield_impact": {"Low": 4.0, "Medium": 11.0, "High": 22.0},
    },
    "gallmidge": {
        "display": "Rice Gall Midge",
        "actions": ["Inspect for silvery tubular galls ('Silver shoots' or 'Onion leaves')", "Check nursery beds before transplanting to ensure clean seedlings"],
        "prevention": ["Adopt early sowing / transplanting to escape peak pest period", "Apply balanced fertilizers with adequate potash to toughen plant tissue"],
        "pesticides": ["Fipronil 0.3% GR @ 7-10 kg/acre in standing water", "Chlorpyrifos 20% EC @ 500 ml/acre in vegetative stage"],
        "organic": ["Neem cake application at planting @ 100 kg/acre", "Conserve parasitoids like Platygaster oryzae"],
        "yield_impact": {"Low": 5.0, "Medium": 13.0, "High": 26.0},
    },
    "blast": {
        "display": "Rice Blast (Leaf / Neck Blast)",
        "actions": ["Examine leaves for spindle-shaped lesions with ash-grey centers", "Check panicle neck nodes for blackish rotting lesions ('Neck Blast')"],
        "prevention": ["Avoid heavy doses of nitrogen fertilizers during cool, humid spells", "Maintain continuous shallow water layer (avoid intermittent drought stress)", "Treat seeds with Carbendazim 2g/kg or Trichoderma viride 5g/kg"],
        "pesticides": ["Tricyclazole 75% WP @ 120-160 g/acre in 200L water", "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 200 ml/acre", "Isoprothiolane 40% EC @ 300 ml/acre"],
        "organic": ["Pseudomonas fluorescens 0.5% liquid spray @ 5 ml/L water", "Spray cow urine extract (10%) with neem oil"],
        "yield_impact": {"Low": 7.0, "Medium": 18.0, "High": 38.0},
    },
    "whitefly": {
        "display": "Whiteflies",
        "actions": ["Install yellow sticky traps @ 10 traps/acre at canopy height", "Inspect lower surfaces of mature leaves for nymphs and puparia"],
        "prevention": ["Remove and burn alternate weed hosts (Abutilon, Sida spp.) on field borders", "Avoid resurgence-causing insecticides like pyrethroids and acephate"],
        "pesticides": ["Diafenthiuron 50% WP @ 240 g/acre", "Pyriproxyfen 10% + Clothianidin 10% EC @ 200 ml/acre", "Afidopyropen 50 g/L DC @ 400 ml/acre"],
        "organic": ["Neem oil 10,000 ppm @ 2-3 ml/L water + detergent wetting agent (0.5 ml/L)", "Lecanicillium lecanii biopesticide @ 5 g/L"],
        "yield_impact": {"Low": 5.0, "Medium": 12.0, "High": 24.0},
    },
    "jassid": {
        "display": "Jassids (Leafhoppers)",
        "actions": ["Inspect third leaf from top on 20 random plants for wedge-shaped nymphs", "Check for marginal leaf yellowing and 'hopper burn' curl"],
        "prevention": ["Use recommended hairy/resistant crop cultivars", "Avoid early moisture stress followed by high fertilizer application"],
        "pesticides": ["Flonicamid 50% WG @ 60-80 g/acre in 200L water", "Dinotefuran 20% SG @ 60-80 g/acre", "Thiamethoxam 25% WG @ 40 g/acre"],
        "organic": ["5% NSKE (Neem Seed Kernel Extract) spray", "Verticillium lecanii @ 5 g/L"],
        "yield_impact": {"Low": 4.0, "Medium": 10.0, "High": 20.0},
    },
    "thrips": {
        "display": "Thrips",
        "actions": ["Inspect seedling growing tips and leaf curls using a white paper tap method", "Look for upward curling and silvery streaks on cotton/rice seedlings"],
        "prevention": ["Maintain weed-free field boundaries and avoid continuous dry spells", "Seed treatment with Imidacloprid 70% WS @ 5-7 g/kg seed"],
        "pesticides": ["Spinetoram 11.7% SC @ 160-180 ml/acre", "Fipronil 5% SC @ 400 ml/acre", "Acephate 75% SP @ 300 g/acre"],
        "organic": ["Neem oil 1500 ppm @ 3 ml/L", "Lecanicillium lecanii @ 5 g/L spray"],
        "yield_impact": {"Low": 3.0, "Medium": 9.0, "High": 18.0},
    },
    "mealybug": {
        "display": "Mealybugs",
        "actions": ["Scout field borders and stems for waxy white clustered colonies", "Look for attending ant movements indicating concealed colonies"],
        "prevention": ["Band plant stems with sticky tanglefoot or grease bands 15 cm above soil", "Destroy Parthenium and other weed hosts around field margins"],
        "pesticides": ["Buprofezin 25% SC @ 400 ml/acre in 200L water with sticking agent", "Profenofos 50% EC @ 500 ml/acre"],
        "organic": ["Release predator Cryptolaemus montrouzieri beetles @ 600/acre", "Drench stem with Neem formulation @ 5 ml/L mixed with soap powder 1 g/L"],
        "yield_impact": {"Low": 5.0, "Medium": 14.0, "High": 30.0},
    },
}

_DEFAULT_RULES = {
    "display": "General Field Pest",
    "actions": [
        "Conduct systematic field scouting across 20 random spots",
        "Install yellow/blue sticky traps and pheromone traps for monitoring",
        "Check crop canopy and soil surface for early signs of infestation",
    ],
    "prevention": [
        "Maintain balanced N-P-K fertilizer split application",
        "Ensure optimal field drainage and proper aeration between rows",
        "Use certified treated seeds with crop rotation practices",
    ],
    "pesticides": [
        "Targeted broad-spectrum contact insecticide if ETL exceeded",
        "Consult local Krishi Vigyan Kendra (KVK) for area-specific chemicals",
    ],
    "organic": [
        "Neem Oil Formulation (Azadirachtin 10,000 ppm) @ 2-3 ml/L water",
        "Pseudomonas fluorescens / Trichoderma bio-agent spray @ 5 g/L",
    ],
    "yield_impact": {"Low": 5.0, "Medium": 12.0, "High": 25.0},
}

_URGENCY_BY_RISK = {
    "High": "CRITICAL: Inspect the field immediately within 24 hours. Pest pressure is elevated.",
    "Medium": "MODERATE: Inspect target crop zones within 48 hours to assess Economic Threshold Level (ETL).",
    "Low": "PREVENTATIVE: Routine weekly crop monitoring. Maintain standard prophylactic hygiene.",
}


def _match_pest_rules(pest_name: str) -> dict:
    pest_clean = (pest_name or "").lower().replace("_", " ").replace("-", " ")
    for keyword, rules in _PEST_RULES.items():
        if keyword in pest_clean:
            return rules
    return _DEFAULT_RULES


def generate_smart_advisory(
    crop: str,
    top_pest: str,
    risk_level: str,
    pests_ranked: list[dict] | None = None,
    weather_dict: dict | None = None,
) -> dict:
    """
    Generates a structured, segregated Smart Advisory for farmers:
    1. Crop Nutrition & Fertilizer Guidance (isolated from chemicals)
    2. Pest Management & Action Plan (Cultural, Biological, Chemical with dosage warnings)
    3. Weather & Spray Timing Guidance
    """
    crop_clean = "Cotton" if "cotton" in (crop or "").lower() else "Rice"
    risk = risk_level if risk_level in ["High", "Medium", "Low"] else "Medium"
    rules = _match_pest_rules(top_pest)
    urgency = _URGENCY_BY_RISK.get(risk, _URGENCY_BY_RISK["Medium"])

    weather = weather_dict or {}
    rf = float(weather.get("RF") or 0.0)
    ws = float(weather.get("WS") or 5.0)
    max_t = float(weather.get("MaxT") or 32.0)
    rh1 = float(weather.get("RH1") or 75.0)

    # 1. Segregated Fertilizer & Nutrition Guidance
    if crop_clean == "Rice":
        if "blast" in (top_pest or "").lower() or "brownplanthopper" in (top_pest or "").lower():
            fert_strategy = (
                "TEMPORARILY WITHHOLD NITROGEN (Urea) top-dressing while pest/disease pressure is active. "
                "Excess soluble nitrogen promotes succulent tissues vulnerable to fungal penetration and hopper buildup. "
                "Apply Muriate of Potash (MOP) @ 15-20 kg/acre to strengthen cell walls."
            )
        else:
            fert_strategy = (
                "Maintain recommended N-P-K schedule (100:50:50 kg/ha equivalent in splits). "
                "Apply 50% N + 100% P + 50% K as basal. Top-dress remaining Nitrogen in 2 equal splits at active tillering and panicle initiation. "
                "Supplement Zinc Sulphate @ 10 kg/acre if leaf midribs show yellowing."
            )
        fert_micro = "Foliar spray of 19-19-19 (NPK) @ 10 g/L or liquid micronutrient complex at flowering."
    else:  # Cotton
        if "bollworm" in (top_pest or "").lower() or "aphid" in (top_pest or "").lower():
            fert_strategy = (
                "Avoid excessive single-dose urea application which attracts sucking pests and bollworm moths. "
                "Split Nitrogen into 3-4 doses. Apply Magnesium Sulphate @ 10 kg/acre and Boron 20% @ 1 g/L foliar spray to prevent square/boll shedding."
            )
        else:
            fert_strategy = (
                "Follow balanced N:P:K (120:60:60 kg/ha equivalent). "
                "Apply 25% N + full P & K as basal; top dress remaining N in 3 equal splits at 30, 60, and 90 days after sowing."
            )
        fert_micro = "Foliar spray of 2% DAP or 1% Potassium Nitrate (13-0-45) during peak flowering & boll development stages."

    # 2. Weather & Spray Timing Guidance
    spray_ok = True
    spray_notes = []
    if rf > 5.0:
        spray_ok = False
        spray_notes.append(f"Rainfall forecast ({rf} mm expected): DO NOT SPRAY pesticides or apply granular fertilizers today; chemical wash-off will occur.")
    elif rf > 0.0:
        spray_notes.append(f"Light rain possible ({rf} mm): Use a silicone-based sticking/spreading agent (0.5 ml/L) if spraying is unavoidable.")
    else:
        spray_notes.append("Clear weather window suitable for foliar spray application.")

    if ws > 15.0:
        spray_ok = False
        spray_notes.append(f"High wind speeds ({ws} km/h): Avoid spraying to prevent severe spray drift and operator contamination.")
    else:
        spray_notes.append(f"Wind speed is calm ({ws} km/h), ideal for uniform droplet coverage.")

    if max_t > 36.0:
        spray_notes.append(f"High temperature ({max_t}°C): Spray only during early morning (6:30 AM - 9:00 AM) or late evening (4:30 PM - 6:30 PM) to prevent rapid evaporation and plant scorching.")
    else:
        spray_notes.append("Perform foliar sprays in the early morning or evening hours.")

    # 3. Compile full advisory structure
    return {
        "urgency": urgency,
        "riskLevel": risk,
        "crop": crop_clean,
        "targetPest": rules.get("display", clean_pest_name(top_pest)),
        "expectedYieldImpact": rules["yield_impact"].get(risk, rules["yield_impact"]["Medium"]),
        "nutritionAdvisory": {
            "title": "Crop Nutrition & Fertilizer Guidance",
            "strategy": fert_strategy,
            "micronutrients": fert_micro,
            "caution": "Never mix alkaline fertilizers with systemic insecticide formulations in the same spray tank.",
        },
        "pestManagement": {
            "title": "Integrated Pest Management (IPM) Strategy",
            "immediateActions": rules["actions"],
            "preventionMeasures": rules["prevention"],
            "biologicalSolutions": rules["organic"],
            "recommendedPesticides": rules["pesticides"],
            "safetyDisclaimer": "Always verify local registrations and adhere to label dosages, PPE safety protocols, and pre-harvest intervals (PHI).",
        },
        "weatherGuidance": {
            "title": "Spray Timing & Environmental Advisory",
            "sprayRecommended": spray_ok,
            "guidanceNotes": spray_notes,
        },
    }


def get_recommendation(prediction_id: int, db: Session):
    record = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.id == prediction_id)
        .first()
    )

    if not record:
        return None

    from agronomy.growth_stage import calculate_growth_stage
    from agronomy.decision_engine import evaluate_crop_health_and_risk
    from agronomy.recommendation_engine import generate_structured_recommendations

    # If already stored as JSON in advisory_json, return it (enriching if structured_recommendations missing)
    if record.advisory_json:
        try:
            stored = json.loads(record.advisory_json)
            stored["predictionId"] = prediction_id
            if "structured_recommendations" in stored:
                return stored
        except Exception:
            stored = {}
    else:
        stored = {}

    risk = record.risk_level or "Medium"
    weather_dict = {
        "MaxT": record.max_t or 30.0,
        "MinT": record.min_t or 22.0,
        "RH1": record.rh1 or 70.0,
        "RH2": record.rh2 or 50.0,
        "RF": record.rf or 0.0,
        "WS": record.ws or 5.0,
        "SSH": record.ssh or 5.0,
        "EVP": record.evp or 4.0,
    }

    growth_stage_info = calculate_growth_stage(
        planting_date_str=getattr(record, "planting_date", None),
        crop_name=record.crop or "Rice",
    )

    soil_data = {
        "soil_type": record.soil_type or "Loam",
        "soil_moisture": record.soil_moisture,
        "soil_ph": record.soil_ph,
        "soil_n": None,
        "soil_p": None,
        "soil_k": None,
        "irrigation_method": "Standard Furrow / Basin",
    }

    tabular_ml_result = {
        "top_pest": {
            "pest_name": record.pest_name or "General Pest",
            "pest_value": record.pest_value or 5.0,
            "risk_level": risk,
        },
        "pests_ranked": [],
        "forecast_risk": [],
    }

    decision_assessment = evaluate_crop_health_and_risk(
        crop=record.crop or "Rice",
        growth_stage_info=growth_stage_info,
        weather_dict=weather_dict,
        forecast_days=[],
        soil_data=soil_data,
        tabular_ml_result=tabular_ml_result,
        image_diagnosis_result=None,
    )

    structured_recs = generate_structured_recommendations(
        crop=record.crop or "Rice",
        growth_stage_info=growth_stage_info,
        weather_dict=weather_dict,
        forecast_days=[],
        soil_data=soil_data,
        decision_assessment=decision_assessment,
        tabular_ml_result=tabular_ml_result,
        image_diagnosis_result=None,
    )

    advisory = generate_smart_advisory(
        crop=record.crop or "Rice",
        top_pest=record.pest_name or "General Pest",
        risk_level=risk,
        weather_dict=weather_dict,
    )

    advisory["predictionId"] = prediction_id
    advisory["crop"] = record.crop
    advisory["pest"] = record.pest_name
    advisory["riskLevel"] = risk
    advisory["growth_stage_info"] = growth_stage_info
    advisory["decision_assessment"] = decision_assessment
    advisory["structured_recommendations"] = structured_recs
    advisory["suggestedActions"] = advisory["pestManagement"]["immediateActions"]
    advisory["prevention"] = advisory["pestManagement"]["preventionMeasures"]
    advisory["recommendedPesticides"] = advisory["pestManagement"]["recommendedPesticides"]
    advisory["organicAlternatives"] = advisory["pestManagement"]["biologicalSolutions"]

    return advisory