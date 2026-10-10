import React, { useState, useEffect, useRef } from "react";
import { Link, useSearchParams, useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import {
  Loader2,
  ScanLine,
  MapPin,
  Sparkles,
  CloudSun,
  FileDown,
  ClipboardList,
  Navigation,
  Thermometer,
  CloudRain,
  Wind,
  CheckCircle2,
  AlertTriangle,
  RefreshCw,
  Droplets,
  Layers,
  Plus,
  Edit3,
  Trash2,
  Search,
  Check,
  Sun,
  Waves,
  ArrowRight,
  ShieldCheck,
  Compass,
  Calendar,
  Camera,
  ShieldAlert,
  Sprout,
  Activity,
  FlaskConical,
} from "lucide-react";

import RiskBadge from "../components/RiskBadge";
import PestRankCard from "../components/PestRankCard";
import ForecastRiskChart from "../components/ForecastRiskChart";
import SmartAdvisory from "../components/SmartAdvisory";
import PlantModal from "../components/PlantModal";

import * as predictService from "../services/predictService";
import * as weatherService from "../services/weatherService";
import * as plantService from "../services/plantService";
import * as diagnosisService from "../services/diagnosisService";

export default function Predict() {
  const [searchParams] = useSearchParams();
  const plantIdParam = searchParams.get("plantId");
  const navigate = useNavigate();

  // ----------------------------------------------------
  // 1. Plant State & Management
  // ----------------------------------------------------
  const [plants, setPlants] = useState([]);
  const [selectedPlantId, setSelectedPlantId] = useState(plantIdParam ? Number(plantIdParam) : null);
  const [plantsLoading, setPlantsLoading] = useState(true);

  // Plant Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalPlantData, setModalPlantData] = useState(null);

  // ----------------------------------------------------
  // 2. Location & Telemetry State
  // ----------------------------------------------------
  const [coords, setCoords] = useState({ lat: 10.787, lon: 79.1378 }); // default Thanjavur
  const [locationName, setLocationName] = useState("Thanjavur, Tamil Nadu");
  const [locationStatus, setLocationStatus] = useState("default");
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationError, setLocationError] = useState("");

  // Search autocomplete state
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const searchContainerRef = useRef(null);

  // ----------------------------------------------------
  // 3. Live Weather State
  // ----------------------------------------------------
  const [currentWeather, setCurrentWeather] = useState(null);
  const [weatherLoading, setWeatherLoading] = useState(false);
  const [weatherError, setWeatherError] = useState("");

  // ----------------------------------------------------
  // 4. Foliar Diagnosis Attachment
  // ----------------------------------------------------
  const [recentDiagnoses, setRecentDiagnoses] = useState([]);
  const [selectedDiagnosisId, setSelectedDiagnosisId] = useState(null);
  const [selectedDiagnosis, setSelectedDiagnosis] = useState(null);

  // ----------------------------------------------------
  // 5. Assessment Execution & Results State
  // ----------------------------------------------------
  const [analyzing, setAnalyzing] = useState(false);
  const [assessmentResult, setAssessmentResult] = useState(null);
  const resultsRef = useRef(null);

  // Load plants on mount
  useEffect(() => {
    loadPlants();
    loadRecentDiagnoses();
  }, []);

  // Close search dropdown on click outside
  useEffect(() => {
    function handleClickOutside(e) {
      if (searchContainerRef.current && !searchContainerRef.current.contains(e.target)) {
        setShowSearchDropdown(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Fetch weather whenever coordinates change
  useEffect(() => {
    if (coords && coords.lat != null && coords.lon != null) {
      fetchLiveWeather(coords.lat, coords.lon, locationName);
    }
  }, [coords.lat, coords.lon]);

  const loadPlants = async () => {
    setPlantsLoading(true);
    try {
      const data = await plantService.getPlants();
      const list = Array.isArray(data) ? data : [];
      setPlants(list);
      if (list.length > 0) {
        const target = plantIdParam ? list.find((p) => p.id === Number(plantIdParam)) || list[0] : list[0];
        selectPlant(target);
      }
    } catch {
      toast.error("Failed to load registered fields");
    } finally {
      setPlantsLoading(false);
    }
  };

  const loadRecentDiagnoses = async () => {
    try {
      const res = await diagnosisService.getDiagnosisHistory(5);
      const list = res?.history || [];
      setRecentDiagnoses(list);
    } catch {}
  };

  const selectPlant = (plant) => {
    if (!plant) return;
    setSelectedPlantId(plant.id);
    if (plant.latitude && plant.longitude) {
      setCoords({ lat: plant.latitude, lon: plant.longitude });
      if (plant.location_name) {
        setLocationName(plant.location_name);
      }
    }
  };

  const selectedPlant = plants.find((p) => p.id === selectedPlantId) || plants[0] || null;

  // ----------------------------------------------------
  // Geolocation & Weather Operations
  // ----------------------------------------------------
  const detectGPSLocation = () => {
    if (!navigator.geolocation) {
      setLocationError("Geolocation is not supported by your browser.");
      setLocationStatus("denied");
      return;
    }

    setLocationLoading(true);
    setLocationError("");

    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = Number(pos.coords.latitude.toFixed(4));
        const lon = Number(pos.coords.longitude.toFixed(4));
        setCoords({ lat, lon });
        setLocationStatus("gps");

        try {
          const snapshot = await weatherService.getWeatherForCoordinates(lat, lon);
          const resolvedName = snapshot.location?.name || `${lat}°N, ${lon}°E`;
          setLocationName(resolvedName);
          setCurrentWeather(snapshot.weather || null);
          toast.success(`GPS Location Locked: ${resolvedName}`);
        } catch {
          setLocationName(`${lat}°N, ${lon}°E`);
        } finally {
          setLocationLoading(false);
        }
      },
      () => {
        setLocationLoading(false);
        setLocationStatus("denied");
        setLocationError("GPS permission denied. Please search your city/field below.");
        toast.error("GPS access denied. Using manual search.");
      },
      { enableHighAccuracy: true, timeout: 10000, maximumAge: 60000 }
    );
  };

  const fetchLiveWeather = async (lat, lon, label = "") => {
    setWeatherLoading(true);
    setWeatherError("");
    try {
      const snapshot = await weatherService.getWeatherForCoordinates(lat, lon);
      setCurrentWeather(snapshot.weather || null);
      if (snapshot.location?.name && !label) {
        setLocationName(snapshot.location.name);
      }
    } catch {
      setWeatherError("Weather telemetry could not be retrieved for these coordinates.");
    } finally {
      setWeatherLoading(false);
    }
  };

  const handleSearchLocations = async (val) => {
    setSearchQuery(val);
    if (!val || val.trim().length < 2) {
      setSearchResults([]);
      setShowSearchDropdown(false);
      return;
    }

    setSearchLoading(true);
    try {
      const results = await weatherService.searchLocations(val);
      setSearchResults(results || []);
      setShowSearchDropdown(true);
    } catch {
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  const handleSelectSearchResult = (place) => {
    const lat = Number(place.latitude.toFixed(4));
    const lon = Number(place.longitude.toFixed(4));
    setCoords({ lat, lon });
    setLocationName(place.display_name || place.name);
    setLocationStatus("search");
    setShowSearchDropdown(false);
    setSearchQuery("");
    setLocationError("");
    toast.success(`Location set to ${place.name}`);
  };

  // ----------------------------------------------------
  // Plant CRUD Actions
  // ----------------------------------------------------
  const handleOpenAddModal = () => {
    setModalPlantData(null);
    setIsModalOpen(true);
  };

  const handleOpenEditModal = (plant) => {
    setModalPlantData(plant);
    setIsModalOpen(true);
  };

  const handleSavePlant = async (payload) => {
    if (modalPlantData?.id) {
      const updated = await plantService.updatePlant(modalPlantData.id, payload);
      setPlants((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      toast.success("Field details updated successfully");
    } else {
      const created = await plantService.createPlant(payload);
      setPlants((prev) => [created, ...prev]);
      setSelectedPlantId(created.id);
      if (created.latitude && created.longitude) {
        setCoords({ lat: created.latitude, lon: created.longitude });
        if (created.location_name) setLocationName(created.location_name);
      }
      toast.success(`Registered ${created.name} to your farm portfolio!`);
    }
  };

  // ----------------------------------------------------
  // Run Integrated Crop Assessment
  // ----------------------------------------------------
  const handleRunAssessment = async () => {
    if (!selectedPlant) {
      toast.error("Please select or create a plant/field record first.");
      return;
    }

    setAnalyzing(true);
    try {
      const payload = {
        Crop: selectedPlant.crop_type,
        Latitude: coords.lat,
        Longitude: coords.lon,
        location_name: locationName,
        plant_id: selectedPlant.id,
        plant_name: selectedPlant.name,
        crop_variety: selectedPlant.variety,
        planting_date: selectedPlant.planting_date,
        growth_stage: selectedPlant.growth_stage,
        field_name: selectedPlant.field_name,
        field_size: selectedPlant.field_size,
        field_size_unit: selectedPlant.field_size_unit || "acres",
        irrigation_method: selectedPlant.irrigation_method,
        soil_type: selectedPlant.soil_type,
        soil_moisture: selectedPlant.soil_moisture,
        soil_ph: selectedPlant.soil_ph,
        soil_n: selectedPlant.soil_n,
        soil_p: selectedPlant.soil_p,
        soil_k: selectedPlant.soil_k,
        diagnosis_id: selectedDiagnosisId,
      };

      const result = await predictService.runCropAssessment(payload);
      setAssessmentResult(result);
      toast.success(`Crop Assessment Complete: ${result.decision_assessment?.overall_health_status || "Healthy"}`);

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 200);
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Crop assessment failed. Please check weather connection.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="card p-6 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 border border-slate-800 shadow-xl">
        <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
          <div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
              <ScanLine size={13} />
              Unified Crop Assessment & Health Intelligence
            </div>
            <h1 className="text-2xl lg:text-3xl font-bold font-display text-white tracking-tight">
              Crop Health & Multi-Risk Assessment
            </h1>
            <p className="text-sm text-slate-400 mt-1 max-w-2xl">
              Combines field location, planting date, growth stage, live Open-Meteo weather, soil parameters, and foliar vision diagnosis into a comprehensive agricultural evaluation.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <button
              onClick={handleOpenAddModal}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-xs transition flex items-center gap-2 shadow-sm"
            >
              <Plus size={15} className="text-emerald-400" /> New Field
            </button>
            <Link
              to="/app/diagnosis"
              className="px-4 py-2.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-semibold transition flex items-center gap-2"
            >
              <Camera size={15} /> Leaf Vision Scanner
            </Link>
          </div>
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* Field Intelligence & Parameter Configuration Bar */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <div className="grid lg:grid-cols-3 gap-6">
        {/* Field & Crop Card */}
        <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sprout className="w-5 h-5 text-emerald-400" />
              <h3 className="font-bold text-slate-200 text-sm">1. Target Field & Crop</h3>
            </div>
            {selectedPlant && (
              <button
                onClick={() => handleOpenEditModal(selectedPlant)}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium"
              >
                <Edit3 size={13} /> Edit
              </button>
            )}
          </div>

          {plants.length === 0 ? (
            <div className="p-4 rounded-xl bg-slate-950/50 border border-slate-800 text-center space-y-2">
              <p className="text-xs text-slate-400">No field records found.</p>
              <button
                onClick={handleOpenAddModal}
                className="text-xs text-emerald-400 font-bold hover:underline"
              >
                + Register a field now
              </button>
            </div>
          ) : (
            <div className="space-y-3">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Select Active Field</label>
                <select
                  value={selectedPlantId || ""}
                  onChange={(e) => {
                    const found = plants.find((p) => p.id === Number(e.target.value));
                    selectPlant(found);
                  }}
                  className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-sm font-semibold focus:outline-none focus:border-emerald-500"
                >
                  {plants.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.name} ({p.crop_type} {p.variety ? `• ${p.variety}` : ""})
                    </option>
                  ))}
                </select>
              </div>

              {selectedPlant && (
                <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400 flex items-center gap-1">
                      <Calendar size={12} className="text-emerald-400" /> Sowing Date:
                    </span>
                    <span className="font-bold text-slate-200">
                      {selectedPlant.planting_date || "Not Specified"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Crop Age / DAP:</span>
                    <span className="font-bold text-emerald-300">
                      {selectedPlant.days_after_planting !== undefined ? `${selectedPlant.days_after_planting} Days (DAP)` : "Calculated"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Physiological Stage:</span>
                    <span className="font-semibold text-emerald-400 truncate max-w-[150px]">
                      {selectedPlant.growth_stage || "Vegetative"}
                    </span>
                  </div>
                  <div className="flex items-center justify-between pt-1 border-t border-slate-800/60">
                    <span className="text-slate-400">Soil & Irrigation:</span>
                    <span className="text-slate-300 truncate max-w-[160px]">
                      {selectedPlant.soil_type || "Loam"}, {selectedPlant.irrigation_method || "Drip"}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Location & Live Weather Telemetry */}
        <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <MapPin className="w-5 h-5 text-emerald-400" />
              <h3 className="font-bold text-slate-200 text-sm">2. Geolocation & Weather</h3>
            </div>
            <button
              onClick={detectGPSLocation}
              disabled={locationLoading}
              className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium"
            >
              {locationLoading ? <Loader2 size={13} className="animate-spin" /> : <Compass size={13} />}
              GPS Sync
            </button>
          </div>

          <div className="space-y-3">
            {/* Search Autocomplete */}
            <div className="relative" ref={searchContainerRef}>
              <div className="flex items-center px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs">
                <Search size={14} className="text-slate-400 mr-2 shrink-0" />
                <input
                  type="text"
                  placeholder="Search city, district, or coordinates..."
                  value={searchQuery}
                  onChange={(e) => handleSearchLocations(e.target.value)}
                  className="w-full bg-transparent text-slate-100 placeholder-slate-500 focus:outline-none text-xs"
                />
                {searchLoading && <Loader2 size={13} className="animate-spin text-emerald-400 shrink-0" />}
              </div>

              {showSearchDropdown && searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl z-50 overflow-hidden max-h-48 overflow-y-auto">
                  {searchResults.map((place, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSelectSearchResult(place)}
                      className="w-full text-left px-3 py-2 text-xs text-slate-200 hover:bg-slate-800 border-b border-slate-800/60 flex items-center justify-between"
                    >
                      <span className="truncate">{place.display_name || place.name}</span>
                      <span className="text-[10px] text-emerald-400 shrink-0 ml-2">Select</span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Current Weather Snapshot */}
            <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-2">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400 truncate max-w-[170px]">{locationName}</span>
                <span className="text-[10px] uppercase font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">
                  LIVE WEATHER
                </span>
              </div>

              <div className="grid grid-cols-4 gap-1.5 text-center pt-1">
                <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[9px] text-slate-400">Temp</div>
                  <div className="text-xs font-bold text-slate-100">
                    {currentWeather?.MaxT ? `${Math.round(currentWeather.MaxT)}°C` : "—"}
                  </div>
                </div>
                <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[9px] text-slate-400">RH</div>
                  <div className="text-xs font-bold text-slate-100">
                    {currentWeather?.RH1 ? `${Math.round(currentWeather.RH1)}%` : "—"}
                  </div>
                </div>
                <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[9px] text-slate-400">Rain</div>
                  <div className="text-xs font-bold text-slate-100">
                    {currentWeather?.RF !== undefined ? `${currentWeather.RF}mm` : "—"}
                  </div>
                </div>
                <div className="p-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <div className="text-[9px] text-slate-400">Wind</div>
                  <div className="text-xs font-bold text-slate-100">
                    {currentWeather?.WS ? `${currentWeather.WS}k/h` : "—"}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Foliar Vision Leaf Diagnosis Attachment */}
        <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Camera className="w-5 h-5 text-emerald-400" />
              <h3 className="font-bold text-slate-200 text-sm">3. Foliar Leaf Diagnosis</h3>
            </div>
            <Link
              to="/app/diagnosis"
              className="text-xs text-emerald-400 hover:text-emerald-300 font-medium flex items-center gap-1"
            >
              + Scan Leaf
            </Link>
          </div>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
                Attach Recent Leaf Scan (Optional)
              </label>
              <select
                value={selectedDiagnosisId || ""}
                onChange={(e) => {
                  const val = e.target.value ? Number(e.target.value) : null;
                  setSelectedDiagnosisId(val);
                  const found = recentDiagnoses.find((d) => d.id === val);
                  setSelectedDiagnosis(found || null);
                }}
                className="w-full px-3.5 py-2.5 bg-slate-950 border border-slate-800 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-emerald-500"
              >
                <option value="">No leaf image attached (Environmental Assessment only)</option>
                {recentDiagnoses.map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.crop_name} • {d.disease_name} ({Math.round(d.confidence)}% conf)
                  </option>
                ))}
              </select>
            </div>

            {selectedDiagnosis ? (
              <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-slate-300 font-bold">{selectedDiagnosis.disease_name}</span>
                  <RiskBadge level={selectedDiagnosis.severity || "Medium"} />
                </div>
                <div className="flex items-center justify-between text-slate-400">
                  <span>Confidence: <strong className="text-emerald-300">{selectedDiagnosis.confidence}%</strong></span>
                  <span>Crop: <strong className="text-slate-200">{selectedDiagnosis.crop_name}</strong></span>
                </div>
              </div>
            ) : (
              <div className="p-3 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-400 space-y-1">
                <p className="text-[11px] text-slate-400">
                  Tip: Upload a leaf photo on the Leaf Scanner page to synthesize foliar pathology with field weather.
                </p>
              </div>
            )}

            {/* Run Assessment Button */}
            <button
              onClick={handleRunAssessment}
              disabled={analyzing || !selectedPlant}
              className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 transition flex items-center justify-center gap-2"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Evaluating Decision Engine...
                </>
              ) : (
                <>
                  <ScanLine size={16} /> Run Complete Crop Assessment
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* Assessment Outcome & Decision Engine Results */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      {assessmentResult && (
        <div ref={resultsRef} className="space-y-6 animate-fadeIn pt-4">
          {/* Main Health Status Banner */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-emerald-500/40 shadow-2xl">
            <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1.5">
                  <span className="px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 flex items-center gap-1.5">
                    <Activity size={13} /> Assessment Outcome
                  </span>
                  <span className="text-xs text-slate-400">
                    Field: <strong className="text-slate-200">{assessmentResult.plant?.name}</strong> ({assessmentResult.crop})
                  </span>
                </div>
                <h2 className="text-2xl font-extrabold text-white">
                  {assessmentResult.decision_assessment?.overall_health_status || "Healthy Condition"}
                </h2>
                <p className="text-sm text-emerald-300/90 mt-1">
                  {assessmentResult.decision_assessment?.health_headline}
                </p>
              </div>

              <div className="flex items-center gap-4 bg-slate-950/60 p-4 rounded-xl border border-slate-800">
                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Overall Risk</span>
                  <RiskBadge level={assessmentResult.decision_assessment?.overall_risk_level || "Low"} />
                </div>
                <div className="border-l border-slate-800 pl-4 text-right">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Crop Age</span>
                  <span className="text-sm font-bold text-slate-100">
                    {assessmentResult.growth_stage_info?.days_after_planting} DAP
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* 3-Column Diagnostic Summary */}
          <div className="grid md:grid-cols-3 gap-5">
            {/* 1. Growth & Demand Profile */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <Sprout size={14} /> Physiological Stage Profile
              </h3>
              <div className="space-y-2 text-xs">
                <div className="p-2.5 rounded-xl bg-slate-950/60 border border-slate-800">
                  <span className="text-slate-400 block text-[10px]">Current Growth Phase</span>
                  <p className="font-bold text-slate-100 text-sm mt-0.5">
                    {assessmentResult.growth_stage_info?.growth_stage}
                  </p>
                  <p className="text-[11px] text-slate-400 mt-1 leading-relaxed">
                    {assessmentResult.growth_stage_info?.stage_description}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-2 text-center pt-1">
                  <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800">
                    <span className="text-[10px] text-slate-400">Water Demand</span>
                    <p className="font-bold text-cyan-400 text-xs mt-0.5">
                      {assessmentResult.growth_stage_info?.water_demand}
                    </p>
                  </div>
                  <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800">
                    <span className="text-[10px] text-slate-400">Nitrogen Demand</span>
                    <p className="font-bold text-emerald-400 text-xs mt-0.5">
                      {assessmentResult.growth_stage_info?.nitrogen_demand}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* 2. Tabular Pest Outbreak Risk */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <ShieldAlert size={14} /> Predictive Pest Pressure (ML)
              </h3>
              <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Top Outbreak Pest:</span>
                  <span className="font-bold text-slate-100">{assessmentResult.top_pest?.pest_name}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Risk Severity:</span>
                  <RiskBadge level={assessmentResult.top_pest?.risk_level || "Low"} />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Pest Incidence Index:</span>
                  <span className="font-mono text-emerald-400 font-bold">
                    {assessmentResult.top_pest?.pest_value ? assessmentResult.top_pest.pest_value.toFixed(1) : "—"}
                  </span>
                </div>
              </div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                Evaluated across 14 meteorological & seasonal field parameters.
              </p>
            </div>

            {/* 3. Foliar Leaf Pathology */}
            <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                <Camera size={14} /> Foliar Pathology (Vision AI)
              </h3>
              {assessmentResult.decision_assessment?.foliar_pathology_assessment?.has_leaf_diagnosis ? (
                <div className="p-3 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Detected Condition:</span>
                    <span className="font-bold text-slate-100">
                      {assessmentResult.decision_assessment.foliar_pathology_assessment.disease}
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Diagnosis Confidence:</span>
                    <span className="font-bold text-emerald-400">
                      {assessmentResult.decision_assessment.foliar_pathology_assessment.confidence}%
                    </span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Pathology Severity:</span>
                    <RiskBadge level={assessmentResult.decision_assessment.foliar_pathology_assessment.severity} />
                  </div>
                </div>
              ) : (
                <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-center space-y-2 text-xs">
                  <p className="text-slate-400">No leaf scan attached for this assessment.</p>
                  <Link to="/app/diagnosis" className="text-emerald-400 font-bold hover:underline inline-block text-[11px]">
                    + Scan a leaf for foliar disease detection
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Environmental Contributing Stress Factors */}
          <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
              <Thermometer size={14} /> Contributing Environmental & Field Factors
            </h3>
            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
              {assessmentResult.contributing_factors?.map((f, idx) => (
                <div key={idx} className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-1.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-200">{f.factor}</span>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                      f.status === "High" || f.status === "Warning" || f.status === "Stressed"
                        ? "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                        : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                    }`}>
                      {f.status}
                    </span>
                  </div>
                  <p className="font-bold text-emerald-300 text-xs">{f.value}</p>
                  <p className="text-[11px] text-slate-400 leading-relaxed">{f.impact}</p>
                  <div className="text-[9px] text-slate-500 pt-1 border-t border-slate-800/60 font-mono">
                    Source: {f.source}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Prioritized Actions Stream Preview */}
          {assessmentResult.recommendations?.prioritized_actions && (
            <div className="bg-slate-900/90 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <div>
                  <h3 className="text-lg font-bold text-slate-100 font-display flex items-center gap-2">
                    <ClipboardList className="w-5 h-5 text-emerald-400" />
                    Prioritized Action Plan (What • When • Why)
                  </h3>
                  <p className="text-xs text-slate-400">
                    Decision-support recommendations tailored to your crop stage, live weather, and risk profile.
                  </p>
                </div>
                <Link
                  to={assessmentResult.prediction_id ? `/app/recommendations?id=${assessmentResult.prediction_id}` : "/app/recommendations"}
                  className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition flex items-center gap-1.5 shadow-md shadow-emerald-500/10"
                >
                  View Full Recommendation Center <ArrowRight size={13} />
                </Link>
              </div>

              <div className="space-y-3">
                {assessmentResult.recommendations.prioritized_actions.slice(0, 3).map((act, idx) => (
                  <div
                    key={idx}
                    className="p-4 rounded-xl bg-slate-950/70 border border-slate-800/90 space-y-2 hover:border-emerald-500/30 transition"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2">
                        <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold uppercase tracking-wider ${
                          act.priority === "CRITICAL"
                            ? "bg-rose-500/15 text-rose-400 border border-rose-500/30"
                            : act.priority === "HIGH"
                            ? "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                            : "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30"
                        }`}>
                          {act.priority}
                        </span>
                        <span className="text-xs font-semibold text-slate-400">[{act.domain}]</span>
                        <h4 className="text-sm font-bold text-slate-100">{act.title}</h4>
                      </div>
                      <span className="text-xs text-emerald-300 font-semibold shrink-0">
                        {act.when}
                      </span>
                    </div>

                    <div className="grid md:grid-cols-2 gap-3 text-xs pt-1">
                      <div>
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">WHAT TO DO</span>
                        <p className="text-slate-200 leading-relaxed">{act.what}</p>
                      </div>
                      <div>
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-0.5">WHY (AGRONOMIC RATIONALE)</span>
                        <p className="text-slate-400 leading-relaxed">{act.why}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 7-Day Outbreak Forecast Chart */}
          {assessmentResult.forecast_risk && assessmentResult.forecast_risk.length > 0 && (
            <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl">
              <h3 className="font-bold text-slate-200 text-sm mb-1 flex items-center gap-2">
                <Activity size={16} className="text-emerald-400" />
                7-Day Environmental Pest Outbreak Risk Timeline
              </h3>
              <p className="text-xs text-slate-400 mb-4">
                Forecasted pest pressure calculated from Open-Meteo 7-day meteorological trends.
              </p>
              <ForecastRiskChart forecastData={assessmentResult.forecast_risk} />
            </div>
          )}

          {/* Data Source Manifest */}
          {assessmentResult.data_sources && (
            <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs space-y-2">
              <h4 className="font-bold text-slate-300 text-[11px] uppercase tracking-wider">
                Transparent Data Source Manifest
              </h4>
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 text-[10px] font-mono text-slate-400">
                {Object.entries(assessmentResult.data_sources).map(([key, val]) => (
                  <div key={key} className="p-1.5 rounded-lg bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block">{key.replace(/_/g, " ")}:</span>
                    <span className="text-emerald-400 font-semibold">{val}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Plant Setup Modal */}
      <PlantModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSavePlant}
        initialData={modalPlantData}
        defaultCoords={coords}
        defaultLocationName={locationName}
      />
    </div>
  );
}
