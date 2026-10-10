# Dataset Card: Crop-Irrigation-AI / AgriSense Multi-Crop Dataset

## 1. Dataset Overview

This dataset card documents the real-world agricultural sensor datasets curated, standardized, and harmonized for **AgriSense / Crop-Irrigation-AI**, a machine learning framework for explainable and uncertainty-aware crop irrigation decision support under climate variability.

In strict adherence to academic research integrity, **zero synthetic measurements or renamed duplicates were introduced**. Every record represents real agrometeorological sensor observations and verified field irrigation events.

---

## 2. Included Data Sources

### Source A: GCEKIoT Smart Agriculture IoT Dataset (2019–2020)
* **Dataset Name:** GCEKIoT Project Datasheet
* **Origin / Affiliation:** Government College of Engineering, Karad (GCEK), Maharashtra, India
* **Location:** Karad, Western Maharashtra, India (Latitude: ~17.28° N, Longitude: ~74.18° E)
* **Time Period:** 2019–2020 cropping seasons
* **Measurement Type:** Edge IoT capacitive soil moisture probes, DHT22 ambient temperature/humidity, DS18B20 soil temperature
* **Crops Covered:**
  * **Paddy (Rice):** 100 observations
  * **Groundnut:** 50 observations
* **Raw Soil Moisture Metric:** Analog Capacitive ADC readings (101 to 768 counts, where 780 counts represents air-dry soil and 100 counts represents water-saturated field capacity)
* **Standardized Metric:** Calibrated Volumetric Water Content (% VWC) via the standard empirical transfer function:
  $$\text{VWC}_{\%} = 10.0 + \left(\frac{780.0 - \text{ADC}}{780.0 - 100.0}\right) \times (45.0 - 10.0)$$
* **Target:** Binary irrigation requirement ($0 = \text{No irrigation needed}, 1 = \text{Irrigation required}$) verified by agronomists.

### Source B: Smart Farming IoT & Crop Sensor Dataset (2024)
* **Dataset Name:** Smart Farming Crop Yield & Sensor Logs 2024
* **Origin / Source:** Kaggle / GitHub Precision Agriculture Research Initiative
* **License:** Open Database License (ODbL) / CC-BY 4.0
* **Location:** Multi-region agricultural stations (North India, South India, South USA, Central USA, East Africa)
* **Time Period:** 2024 cropping cycles
* **Sample Count:** 500 field records
* **Crops Covered:**
  * **Maize:** 111 observations
  * **Soybean:** 108 observations
  * **Cotton:** 107 observations
  * **Wheat:** 92 observations
  * **Rice:** 82 observations
* **Features:**
  * `soil_moisture_%`: Calibrated soil moisture percentage (10.16% to 44.98%)
  * `temperature_C`: Ambient air temperature (°C, 15.0 to 34.84°C)
  * `humidity_%`: Relative air humidity (%, 40.23% to 90.0%)
  * `rainfall_mm`: Rainfall (mm, 50.0 to 300.0 mm)
  * `total_days`: Vegetative cycle elapsed days (90 to 150 days)
  * `irrigation_type`: Sprinkler (121), Manual (118), Drip (111), None (150)
* **Target Mapping:** $0$ if `irrigation_type == None` (no irrigation applied, 150 records), $1$ if `irrigation_type` $\in$ {Sprinkler, Drip, Manual} (irrigation applied, 350 records).

---

## 3. Harmonized Master Dataset (`multi_crop_irrigation.csv`)

* **Total Records:** **650 rows**
* **Supported Crops & Class Balance:**

| Crop Name | Scientific / Common Name | Source Dataset | Negative ($0$) | Positive ($1$) | Total Rows | Proportion |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **Rice / Paddy** | *Oryza sativa* | GCEKIoT & SmartFarming | 109 | 73 | **182** | 28.0% |
| **Maize** | *Zea mays* | SmartFarming-2024 | 31 | 80 | **111** | 17.1% |
| **Soybean** | *Glycine max* | SmartFarming-2024 | 29 | 79 | **108** | 16.6% |
| **Cotton** | *Gossypium hirsutum* | SmartFarming-2024 | 34 | 73 | **107** | 16.5% |
| **Wheat** | *Triticum aestivum* | SmartFarming-2024 | 31 | 61 | **92** | 14.1% |
| **Groundnut** | *Arachis hypogaea* | GCEKIoT-2020 | 41 | 9 | **50** | 7.7% |
| **Total** | — | — | **275** | **375** | **650** | **100.0%** |

### Standardized Feature Schema
1. `crop_name`: Canonical crop string (`Rice`, `Groundnut`, `Wheat`, `Maize`, `Cotton`, `Soybean`)
2. `crop_type`: Integer-encoded crop identifier (0 to 5)
3. `crop_days`: Days elapsed in growth cycle (continuous, 1 to 150 days)
4. `soil_moisture`: Soil volumetric moisture percentage (% VWC, 10.0% to 45.0%)
5. `soil_temperature`: Topsoil temperature (°C, 14.2°C to 29.1°C)
6. `temperature`: Ambient temperature (°C, 15.0°C to 34.8°C)
7. `humidity`: Relative air humidity (%, 40.2% to 90.0%)
8. `rainfall`: Precipitation (mm)
9. `irrigation`: Binary ground-truth target ($0 = \text{No}, 1 = \text{Yes}$)
10. `location`: Geographical origin of observation
11. `dataset_source`: Traceable provenance (`GCEKIoT-2020` or `SmartFarming-IoT-2024`)

---

## 4. Documentation of Excluded Candidate Crops

In compliance with the **Absolute Data Integrity Rule**, the following candidate crops were evaluated but excluded from the active trained model:

| Candidate Crop | Status | Justification & Exclusion Reason |
| :--- | :---: | :--- |
| **Sugarcane** | *Excluded* | Evaluated public datasets either lacked soil moisture sensor telemetry or contained only simulated static irrigation calendar schedules without verified sensor feedback. |
| **Tomato** | *Excluded* | Available open repositories (e.g. Mendeley 2026 Edge IoT) operate on sub-15-minute valve actuator telemetry with electrical conductivity and fertigation lines, lacking matching seasonal vegetative features. |
| **Potato** | *Excluded* | No open-access IoT dataset combining simultaneous soil moisture, ambient humidity, temperature, and verified ground-truth irrigation labels was identified. |
| **Onion** | *Excluded* | Lacks publicly accessible sensor telemetry matching the standardized agrometeorological schema. |
| **Chilli** | *Excluded* | Existing datasets were restricted to image classification (leaf disease detection) rather than soil hydrological measurements. |
| **Banana** | *Excluded* | No compatible open IoT irrigation telemetry available with verified target labels. |
| **Green Gram / Black Gram** | *Excluded* | Limited data points without ground-truth irrigation logs; excluded to avoid synthetic imputation or label guessing. |

---

## 5. Ethical & Scientific Integrity Affirmation

* No data rows were fabricated or synthesized to inflate sample size.
* No records from one crop were relabeled or cloned as another crop.
* Sensor metrics preserve their empirical physical ranges and thermodynamic consistency.
* Cross-validation and test evaluation are conducted on strictly stratified held-out folds with fixed seed (`42`).
