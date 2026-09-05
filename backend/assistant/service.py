import os
from typing import List, Optional

_KNOWLEDGE_BASE = [
    {
        "keywords": ["bollworm", "american bollworm", "pink bollworm", "spotted bollworm"],
        "reply": (
            "🐛 **Bollworm Management Protocol (Cotton)**:\n"
            "• **Identification**: Look for flare-up of squares, bore holes plugged with excreta in bolls, and rosette flowers.\n"
            "• **Immediate Action**: Install 5 pheromone traps/acre for monitoring. Hand-pick visible larvae in early stages.\n"
            "• **Organic Control**: Spray *Bacillus thuringiensis* (Bt) @ 2g/L or 5% Neem Seed Kernel Extract (NSKE).\n"
            "• **Chemical Control**: For high infestation (ETL > 1 larva/plant), spray Emamectin Benzoate 5% SG @ 0.4g/L or Chlorantraniliprole 18.5% SC @ 0.3ml/L.\n"
            "• **Precaution**: Avoid spraying during peak bee activity hours; rotate chemical groups to prevent resistance."
        ),
    },
    {
        "keywords": ["aphid", "aphids", "cotton aphid"],
        "reply": (
            "🌿 **Aphid Control & Treatment (Cotton/Vegetables)**:\n"
            "• **Symptoms**: Curling and crinkling of tender leaves, honeydew secretion with black sooty mold growth.\n"
            "• **Weather Trigger**: Cloudy weather with high relative humidity (>75%) promotes rapid aphid multiplication.\n"
            "• **Biological/Organic**: Spray 2% Neem Oil (20ml/L with soap emulsion) or release *Coccinellid* (Ladybird) predators.\n"
            "• **Chemical Treatment**: Imidacloprid 17.8% SL @ 0.5ml/L or Acetamiprid 20% SP @ 0.2g/L.\n"
            "• **Cultural Practice**: Remove alternative weed hosts around field borders."
        ),
    },
    {
        "keywords": ["whitefly", "whiteflies"],
        "reply": (
            "🪰 **Whitefly Management (Cotton)**:\n"
            "• **Symptoms**: Yellowing of leaf veins, upward curling, transmission of Cotton Leaf Curl Virus (CLCuV).\n"
            "• **Monitoring**: Place yellow sticky traps @ 10-12 traps/acre at canopy height.\n"
            "• **Organic Control**: Neem oil 2% or fish oil rosin soap spray @ 25g/L.\n"
            "• **Chemical Treatment**: Diafenthiuron 50% WP @ 1.2g/L, Pyriproxyfen 10% EC @ 2ml/L, or Thiamethoxam 25% WG @ 0.3g/L.\n"
            "• **Note**: Avoid excessive nitrogenous fertilizers as succulent growth invites higher whitefly populations."
        ),
    },
    {
        "keywords": ["stem borer", "yellow stem borer", "rice borer"],
        "reply": (
            "🌾 **Stem Borer Management (Rice)**:\n"
            "• **Symptoms**: 'Dead hearts' at vegetative stage and 'White ears' (chaffy panicles) at reproductive stage.\n"
            "• **Monitoring**: Set up light traps and pheromone traps (Scirpophaga incertulas lures) @ 5/ha.\n"
            "• **Biological Control**: Release *Trichogramma japonicum* egg parasitoid cards @ 100,000/ha (weekly intervals).\n"
            "• **Chemical Control**: Cartap Hydrochloride 4% G @ 10kg/acre or Chlorantraniliprole 0.4% GR @ 4kg/acre applied with irrigation water.\n"
            "• **Cultural**: Clip seedling leaf tips before transplanting to eliminate egg masses."
        ),
    },
    {
        "keywords": ["brown planthopper", "bph", "plant hopper", "planthopper"],
        "reply": (
            "🌾 **Brown Planthopper (BPH) Protocol (Rice)**:\n"
            "• **Symptoms**: 'Hopper burn' (circular patches of dried, brown plants), lodging, and stunted growth.\n"
            "• **Weather Trigger**: High humidity, dense planting, and standing water create ideal microclimates.\n"
            "• **Immediate Action**: Drain water from the field for 3-4 days (alternate wetting and drying) to break breeding.\n"
            "• **Chemical Treatment**: Pymetrozine 50% WG @ 0.6g/L, Triflumezopyrim 10% SC @ 0.5ml/L, or Dinotefuran 20% SG @ 0.4g/L directed at the base of the plants.\n"
            "• **Caution**: Do not use synthetic pyrethroids as they trigger BPH resurgence."
        ),
    },
    {
        "keywords": ["leaf folder", "rice leaf folder", "leaffolder"],
        "reply": (
            "🍃 **Rice Leaf Folder Control**:\n"
            "• **Symptoms**: Longitudinal leaf folding with white, transparent scratch marks caused by scraping larvae.\n"
            "• **ETL (Economic Threshold)**: 10% folded leaves at vegetative stage or 5% at flowering.\n"
            "• **Treatment**: Spray Cartap Hydrochloride 50% SP @ 1g/L or Flubendiamide 39.35% SC @ 0.2ml/L.\n"
            "• **Organic**: Release *Trichogramma chilonis* cards @ 5/ha."
        ),
    },
    {
        "keywords": ["neem", "organic", "bio pesticide", "biopesticide", "natural control"],
        "reply": (
            "🌱 **Organic & Biological Pest Management Strategy**:\n"
            "1. **Neem Oil 2% Formulation**: Mix 20ml cold-pressed neem oil + 2ml liquid dish soap per 1 liter water. Effective against sucking pests (aphids, thrips, whiteflies).\n"
            "2. **Pheromone & Sticky Traps**: Yellow sticky traps for whiteflies/aphids; species-specific pheromone lures for bollworms and stem borers.\n"
            "3. **Predator Conservation**: Conserve ladybird beetles, hoverflies, and spiders by avoiding broad-spectrum chemical sprays.\n"
            "4. **Botanical Extracts**: 5% Neem Seed Kernel Extract (NSKE) or 3% Panchagavya foliar spray for enhanced crop resistance."
        ),
    },
    {
        "keywords": ["humidity", "rain", "rainfall", "temperature", "weather", "forecast"],
        "reply": (
            "⛅ **Weather & Pest Relationship Guide**:\n"
            "• **High Humidity (RH1 > 80%)**: Strongly accelerates fungal growth and rapid multiplication of sucking pests (aphids, BPH).\n"
            "• **High Temperature (MaxT > 35°C)**: Shortens pest generation cycles, increasing the frequency of reproduction.\n"
            "• **Continuous Light Rains (RF 20-50mm)**: Softens plant tissues, creating entry points for larvae and borers.\n"
            "• **Wind Speed (WS > 15 km/h)**: Aids long-distance migration of winged aphids, whiteflies, and planthoppers.\n"
            "• **Recommendation**: Run an AI Prediction on AgriShield with this week's weather snapshot to evaluate real-time outbreak probability."
        ),
    },
    {
        "keywords": ["cotton"],
        "reply": (
            "🌾 **Cotton Crop Protection Overview**:\n"
            "• Major Pests: Bollworm complex, Aphids, Whiteflies, Jassids, and Thrips.\n"
            "• Critical Stages: Squaring (Week 6-8) and Boll Formation (Week 10-14) require maximum vigilance.\n"
            "• Prevention: Maintain balanced nitrogen fertilization, install pheromone traps, and scout leaf undersides weekly."
        ),
    },
    {
        "keywords": ["rice", "paddy"],
        "reply": (
            "🌾 **Rice (Paddy) Protection Overview**:\n"
            "• Major Pests: Yellow Stem Borer, Brown Planthopper (BPH), Leaf Folder, and Gall Midge.\n"
            "• Critical Stages: Active tillering and panicle initiation are most vulnerable to stem borer and BPH.\n"
            "• Prevention: Practice alternate wetting and drying (AWD) irrigation and avoid excess urea application."
        ),
    },
]


def _gemini_chat_response(message: str, history: Optional[List[dict]] = None) -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        system_instruction = (
            "You are AgriShield AI Agronomist, a world-class precision agricultural consultant "
            "specializing in predictive pest management, integrated pest management (IPM), weather-pest correlations, "
            "and crop protection for Cotton and Rice crops. Provide precise, actionable agronomic advice with dosage, "
            "organic options, and safety guidelines. Keep answers structured, practical, and clear for farmers."
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=message,
            config={"system_instruction": system_instruction},
        )
        if response and response.text:
            return response.text.strip()
    except Exception:
        pass
    return None


def get_ai_response(message: str, history: Optional[List[dict]] = None) -> str:
    # 1. Check if Gemini API is configured
    gemini_reply = _gemini_chat_response(message, history)
    if gemini_reply:
        return gemini_reply

    # 2. Intelligent Agronomic Knowledge Base Matching
    cleaned = message.lower().strip()

    if not cleaned:
        return "Hello! I am AgriShield AI Assistant. How can I help you with your crops, pest control, or weather management today?"

    # Match best knowledge base topic
    for entry in _KNOWLEDGE_BASE:
        if any(kw in cleaned for kw in entry["keywords"]):
            return entry["reply"]

    # Greetings
    if any(g in cleaned for g in ["hello", "hi", "hey", "namaste", "help", "who are you"]):
        return (
            "👋 Hello! I am **AgriShield AI Assistant**, your crop protection and pest intelligence advisor.\n\n"
            "You can ask me about:\n"
            "• **Pest Protocols**: Bollworms, Aphids, Whiteflies, Stem Borers, Brown Planthoppers, Leaf Folders.\n"
            "• **Treatments**: Chemical dosages, biological alternatives (*Bt*, *Trichogramma*), and Neem oil formulations.\n"
            "• **Weather Impact**: How humidity, rainfall, and temperature trigger outbreaks.\n"
            "• **Predictions**: Interpreting pest risk scores and PDF reports."
        )

    # General agronomy fallback
    return (
        "🌱 **AgriShield Agronomic Advisor**:\n"
        "For optimal crop health, monitor fields twice weekly, scout leaf undersides, and check regional weather patterns. "
        "High humidity (>70%) paired with moderate temperatures is the primary trigger for rapid pest reproduction.\n\n"
        "To get an exact pest pressure forecast for your field, run a prediction from the **AI Prediction** tab!"
    )