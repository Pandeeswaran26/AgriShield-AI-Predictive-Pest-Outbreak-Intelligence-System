# Walkthrough: AgriShield AI Agricultural Decision-Support System

We have redesigned and reorganized **AgriShield AI** from a siloed prediction app into a cohesive, explainable **Agricultural Decision-Support System**.

---

## 1. System Architecture

```
                                  AGRISHIELD AI
                                        │
              ┌─────────────────────────┴─────────────────────────┐
              │                                                   │
    [ FIELD INTELLIGENCE ]                               [ PLANT VISION AI ]
              │                                                   │
    • Crop & Field Geolocation (GPS/Search)              • Upload / Camera Capture
    • Sowing Date -> Dynamic DAP & Growth Stage          • Multi-Factor Leaf Validation Gate
    • Live Weather (Open-Meteo API: T, RH, RF, WS)       • 38-Class Disease & Health Classifier
    • Soil Context (Moisture, pH, NPK if provided)       • Content-Derived Confidence %
              │                                                   │
              └─────────────────────────┬─────────────────────────┘
                                        │
                         [ AGRISHIELD DECISION ENGINE ]
                                        │
          ┌─────────────────────────────┼─────────────────────────────┐
          │                             │                             │
    [ Tabular ML Risk ]         [ Foliar Pathology ]        [ Environmental Stress ]
    Pest Outbreak Pressure       Active Disease Symptoms     Heat, Moisture, Rain Wash-off
          │                             │                             │
          └─────────────────────────────┼─────────────────────────────┘
                                        │
                        [ AI RECOMMENDATION ENGINE ]
                                        │
       ┌────────────────┬───────────────┴────────────────┬────────────────┐
       ▼                ▼                                ▼                ▼
 [ IRRIGATION ]   [ FERTILIZER ]                  [ DISEASE / PEST ]  [ WEATHER / TIMING ]
 • Status          • Growth Stage Demand           • Targeted IPM      • Spray Window
 • Time Window     • Soil NPK Analysis             • Biological/Chem   • Rain Wash-off Alert
 • Agronomic Why   • Missing Test Warnings         • Urgency & Actions • Heat Stress Timing
       │                │                                │                │
       └────────────────┴───────────────┬────────────────┴────────────────┘
                                        │
                           [ PRIORITIZED ACTIONS ]
                        CRITICAL • HIGH • MEDIUM • LOW
                     (WHAT TO DO • WHEN TO DO IT • WHY)
                                        │
              ┌─────────────────────────┴─────────────────────────┐
              ▼                                                   ▼
   [ My Fields / Dashboard ]                             [ Crop Assessment & Details ]
```

---

## 2. Implemented Components

### A. Agronomy & Decision Engine (`backend/agronomy/`)
1. **Growth Stage & DAP Engine ([`growth_stage.py`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/backend/agronomy/growth_stage.py))**:
   - Calculates **Days After Planting (DAP)** dynamically from `planting_date`.
   - Maps crop growth schedules across 9 major crop families (Rice, Cotton, Tomato, Potato, Corn, Wheat, Apple, Grape, Pepper).
   - Generates water and nutrient demand profiles per physiological stage (`CALCULATED (ESTIMATE)`).
2. **Central Decision Engine ([`decision_engine.py`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/backend/agronomy/decision_engine.py))**:
   - Synthesizes Field Data + Growth Stage + Live Weather + Tabular Outbreak Risk + Foliar Vision Pathology.
   - Evaluates thermal oscillation, foliar humidity windows, precipitation wash-off risks, and soil stress.
   - Assigns multi-domain health status (`Healthy`, `Moderate Environmental Stress`, `Active Disease Infection`, `Pest Outbreak Alert`).
   - Maintains a **Transparent Data Source Manifest** tagging every metric (`LIVE WEATHER`, `USER INPUT`, `CALCULATED`, `IMAGE MODEL`, `ML MODEL`, `DECISION ENGINE`).
3. **Structured Recommendation Engine ([`recommendation_engine.py`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/backend/agronomy/recommendation_engine.py))**:
   - Produces prioritized decisions with explicit **WHAT TO DO**, **WHEN TO DO IT**, and **WHY**.
   - **Irrigation**: Computes status (`Irrigate now`, `Irrigate soon`, `No irrigation currently`, `Recheck later`), time windows, and soil moisture / rain forecast rationale.
   - **Fertilizer**: Evaluates crop requirement at current stage, checks soil NPK/pH, and issues an explicit warning if lab soil tests are missing (*"Recommendation limited because soil nutrient measurements are unavailable"*).
   - **Disease/Pest IPM**: Confidence-gated treatments; prevents heavy chemical recommendations if diagnosis confidence is low (<50%).
   - **Weather & Spray Timing**: Recommends foliar spray windows based on wind velocity (<15 km/h), rain risk, and heat-stress avoidance.

---

### B. Database Schema & Backend APIs
1. **Database Enhancements ([`database.py`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/backend/database/database.py), [`models.py`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/backend/plants/models.py), [`history/models.py`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/backend/history/models.py))**:
   - Added `irrigation_method`, `soil_n`, `soil_p`, `soil_k`, `last_assessment_date`, `last_health_status`, `last_risk_level`, `last_recommended_action` to `plants` table.
   - Added `diagnosis_id`, `health_status`, `data_sources_json` to `prediction_history` table.
   - Automated schema migration utility `ensure_migrations(engine)` ensures zero data loss across PostgreSQL & SQLite.
2. **Unified API Endpoints ([`main.py`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/backend/app/main.py))**:
   - `POST /api/assessment/run` (and `/predict/auto`): Executes full crop assessment with decision & recommendation engines.
   - `GET /dashboard/fields`: Returns operational field overview with live weather, DAP, growth stage, health status, and top next action.
   - `GET /recommendations/{id}`: Exposes structured WHAT/WHEN/WHY recommendations.

---

### C. Frontend Redesign (`agrishield-frontend/src/`)
1. **Dashboard ([`Dashboard.jsx`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/agrishield-frontend/src/pages/Dashboard.jsx))**:
   - Redesigned around **"My Fields & Crop Health Surveillance"**.
   - Displays real farmer fields as operational cards showing crop, variety, DAP, growth stage, live weather telemetry, health status, risk level, and next prioritized action.
   - Quick action to run assessments directly for any field.
2. **Crop Assessment Hub ([`Predict.jsx`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/agrishield-frontend/src/pages/Predict.jsx))**:
   - Field selection / setup with auto-loading of sowing date, calculated DAP, growth stage, soil type, and coordinates.
   - Live Open-Meteo weather telemetry widget with GPS sync and search autocomplete.
   - Foliar Leaf Diagnosis attachment dropdown (optionally link recent leaf scan).
   - Unified diagnostic outcome with Health Status Banner, Physiological Demand, Contributing Stress Factors, and Prioritized Actions stream.
   - Transparent Data Source tags on all inputs and metrics.
3. **AI Decision Center ([`Recommendation.jsx`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/agrishield-frontend/src/pages/Recommendation.jsx))**:
   - Prioritized Action Stream (`CRITICAL`, `HIGH`, `MEDIUM`, `LOW`) with concrete WHAT, WHEN, and WHY blocks.
   - 4 Domain Decision Panels: Irrigation Intelligence, Crop Nutrition & Fertilizer (with missing soil test alert), Weather & Spray Timing Window, and Targeted IPM.
   - Executive PDF Report export.
4. **Plant Setup Modal ([`PlantModal.jsx`](file:///c:/Users/Pandeeswaran%20B/OneDrive/Desktop/AgriShield-AI/agrishield-frontend/src/components/PlantModal.jsx))**:
   - Sowing date picker with live DAP and growth stage calculation preview.
   - Irrigation method selector and optional Soil Test N-P-K inputs.

---

## 3. Verification & Test Results

| Test Suite | Components Tested | Status |
| :--- | :--- | :--- |
| **`test_decision_support_flow.py`** | Growth stage engine, enhanced Plant CRUD, Decision Engine, Recommendation Engine (WHAT/WHEN/WHY), Dashboard fields API | **PASSED** (All 5 steps) |
| **`test_db_flow.py`** | User auth, Plant CRUD, Open-Meteo live weather, Tabular ML inference, History persistence | **PASSED** |
| **`test_diagnosis_flow.py`** | Spectral leaf validation gate, 38-class leaf vision classifier, non-plant image rejection | **PASSED** |
| **Frontend Production Build (`npm run build`)** | React + Vite client bundle compilation | **PASSED** (0 errors, 2,869 modules) |

---

## 4. Key Agronomic Boundaries Respected
1. **Transparent Data Sources**: Every metric displayed to the user indicates whether it is `LIVE WEATHER`, `USER INPUT`, `CALCULATED (ESTIMATE)`, `IMAGE MODEL`, `ML MODEL`, or `DECISION ENGINE`.
2. **Missing Data Handling**: Soil NPK and pH default to `NOT PROVIDED` when unavailable, triggering conservative growth-stage baselines and explicit warnings rather than fabricated measurements.
3. **Preservation of Core Assets**: Tabular ExtraTrees model (`ml/models/final_pest_prediction_model.pkl`) and the 38-class plant vision model remain intact and seamlessly orchestrated.
