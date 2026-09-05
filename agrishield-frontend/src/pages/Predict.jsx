import React, { useState, useEffect, useRef } from "react";
import { Link } from "react-router-dom";
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
} from "lucide-react";

import RiskBadge from "../components/RiskBadge";
import PestRankCard from "../components/PestRankCard";
import ForecastRiskChart from "../components/ForecastRiskChart";
import SmartAdvisory from "../components/SmartAdvisory";
import PlantModal from "../components/PlantModal";

import * as predictService from "../services/predictService";
import * as weatherService from "../services/weatherService";
import * as plantService from "../services/plantService";

export default function Predict() {
  // ----------------------------------------------------
  // 1. Plant State & Management
  // ----------------------------------------------------
  const [plants, setPlants] = useState([]);
  const [selectedPlantId, setSelectedPlantId] = useState(null);
  const [plantsLoading, setPlantsLoading] = useState(true);

  // Plant Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalPlantData, setModalPlantData] = useState(null);

  // ----------------------------------------------------
  // 2. Location & Telemetry State
  // ----------------------------------------------------
  const [coords, setCoords] = useState({ lat: 10.787, lon: 79.1378 }); // default Thanjavur / initial center
  const [locationName, setLocationName] = useState("Thanjavur, Tamil Nadu");
  const [locationStatus, setLocationStatus] = useState("default"); // 'gps', 'search', 'manual', 'denied', 'error'
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
  // 4. Prediction Execution & Results State
  // ----------------------------------------------------
  const [analyzing, setAnalyzing] = useState(false);
  const [predictionData, setPredictionData] = useState(null);
  const [forecastRisk, setForecastRisk] = useState([]);
  const [pestsRanked, setPestsRanked] = useState([]);
  const [smartAdvisory, setSmartAdvisory] = useState(null);
  const resultsRef = useRef(null);

  // Load plants on mount
  useEffect(() => {
    loadPlants();
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
      if (list.length > 0 && !selectedPlantId) {
        // Select first plant by default
        selectPlant(list[0]);
      }
    } catch {
      toast.error("Failed to load your registered plants");
    } finally {
      setPlantsLoading(false);
    }
  };

  const selectPlant = (plant) => {
    setSelectedPlantId(plant.id);
    // If the plant has saved field coordinates, update active location
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
      (err) => {
        setLocationLoading(false);
        setLocationStatus("denied");
        setLocationError("GPS permission denied or unavailable. You can search any city/farm below.");
        toast.error("GPS access denied. Using manual location search.");
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
    } catch (err) {
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
      // Update
      const updated = await plantService.updatePlant(modalPlantData.id, payload);
      setPlants((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
      toast.success("Plant details updated successfully");
    } else {
      // Create
      const created = await plantService.createPlant(payload);
      setPlants((prev) => [created, ...prev]);
      setSelectedPlantId(created.id);
      if (created.latitude && created.longitude) {
        setCoords({ lat: created.latitude, lon: created.longitude });
        if (created.location_name) setLocationName(created.location_name);
      }
      toast.success(`Added ${created.name} to your farm portfolio!`);
    }
  };

  const handleDeletePlant = async (plantId, plantName) => {
    if (!window.confirm(`Are you sure you want to delete "${plantName}"?`)) return;
    try {
      await plantService.deletePlant(plantId);
      const filtered = plants.filter((p) => p.id !== plantId);
      setPlants(filtered);
      if (selectedPlantId === plantId && filtered.length > 0) {
        selectPlant(filtered[0]);
      }
      toast.success("Plant record removed");
    } catch {
      toast.error("Failed to delete plant record");
    }
  };

  // ----------------------------------------------------
  // Run AI Pest Outbreak Prediction
  // ----------------------------------------------------
  const handleRunPrediction = async () => {
    if (!selectedPlant) {
      toast.error("Please add or select a plant first.");
      return;
    }
    if (!coords || coords.lat == null || coords.lon == null) {
      toast.error("Please specify a valid field location.");
      return;
    }

    setAnalyzing(true);
    setPredictionData(null);
    setPestsRanked([]);
    setForecastRisk([]);
    setSmartAdvisory(null);

    try {
      const payload = {
        Crop: selectedPlant.crop_type || "Rice",
        Latitude: coords.lat,
        Longitude: coords.lon,
        plant_id: selectedPlant.id,
        plant_name: selectedPlant.name,
        crop_variety: selectedPlant.variety,
        growth_stage: selectedPlant.growth_stage,
        field_name: selectedPlant.field_name,
        field_size: selectedPlant.field_size,
        field_size_unit: selectedPlant.field_size_unit,
        soil_type: selectedPlant.soil_type,
        soil_moisture: selectedPlant.soil_moisture,
        soil_ph: selectedPlant.soil_ph,
        location_name: locationName,
      };

      const data = await predictService.predictPestAuto(payload);
      setPredictionData(data);
      setPestsRanked(data.pests_ranked || []);
      setForecastRisk(data.forecast_risk || []);
      setSmartAdvisory(data.smart_advisory || null);

      if (data.current_weather) {
        setCurrentWeather(data.current_weather);
      }

      toast.success("AI pest risk modeling completed!");

      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: "smooth" });
      }, 200);
    } catch (err) {
      const detail = err.response?.data?.detail;
      toast.error(typeof detail === "string" ? detail : "Failed to run prediction. Please verify inputs.");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-7 max-w-7xl mx-auto pb-12">
      {/* Top Header Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Sparkles className="w-3.5 h-3.5" />
            Predictive Pest Outbreak Intelligence System
          </div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-100 flex items-center gap-2.5">
            Dynamic Agricultural Prediction Hub
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Select your plant, synchronize live atmospheric telemetry, and trigger the trained multi-species ML risk pipeline.
          </p>
        </div>

        <button
          onClick={handleOpenAddModal}
          className="self-start md:self-auto py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 transition flex items-center gap-2"
        >
          <Plus className="w-4 h-4" />
          Add New Plant
        </button>
      </div>

      {/* 7-Step Visual Workflow Breadcrumbs */}
      <div className="bg-slate-900/60 p-3.5 rounded-2xl border border-slate-800/80 overflow-x-auto">
        <div className="flex items-center gap-2 text-xs font-medium text-slate-400 min-w-[680px]">
          <span className={`flex items-center gap-1.5 ${selectedPlant ? "text-emerald-400 font-semibold" : ""}`}>
            <span className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[11px] font-bold">
              1
            </span>
            Select / Add Plant
          </span>
          <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
          <span className="flex items-center gap-1.5 text-slate-300">
            <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[11px] font-bold">
              2
            </span>
            Agronomic Details
          </span>
          <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
          <span className={`flex items-center gap-1.5 ${locationStatus !== "error" ? "text-emerald-400" : ""}`}>
            <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[11px] font-bold">
              3
            </span>
            Field GPS / Search
          </span>
          <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
          <span className={`flex items-center gap-1.5 ${currentWeather ? "text-emerald-400" : ""}`}>
            <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[11px] font-bold">
              4
            </span>
            Live Open-Meteo
          </span>
          <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
          <span className="flex items-center gap-1.5 text-slate-300">
            <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[11px] font-bold">
              5
            </span>
            Review Inputs
          </span>
          <ArrowRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
          <span className={`flex items-center gap-1.5 ${predictionData ? "text-emerald-400 font-bold" : ""}`}>
            <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[11px] font-bold">
              6
            </span>
            ML Outbreak Prediction
          </span>
        </div>
      </div>

      {/* ======================================================== */}
      {/* SECTION 1: DYNAMIC PLANT MANAGEMENT & CARD SELECTOR     */}
      {/* ======================================================== */}
      <div className="bg-slate-900/80 p-5 md:p-6 rounded-2xl border border-slate-800 space-y-4 shadow-xl">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div>
            <h2 className="font-bold text-slate-100 text-base md:text-lg flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-400" />
              1 & 2. My Plant Records & Field Conditions
            </h2>
            <p className="text-xs text-slate-400 mt-0.5">
              Choose an existing plant or register a new crop to customize soil parameters, variety, and growth stage.
            </p>
          </div>
          <button
            onClick={handleOpenAddModal}
            className="text-xs font-semibold px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/20 flex items-center gap-1.5 transition self-start sm:self-auto"
          >
            <Plus className="w-3.5 h-3.5" />
            Add New Plant
          </button>
        </div>

        {plantsLoading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-3 text-slate-400 text-xs">
            <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
            Loading your farm portfolio...
          </div>
        ) : plants.length === 0 ? (
          <div className="py-10 px-4 rounded-xl bg-slate-950/40 border border-dashed border-slate-800 text-center space-y-3">
            <div className="w-12 h-12 rounded-full bg-emerald-500/10 text-emerald-400 flex items-center justify-center mx-auto">
              <Plus className="w-6 h-6" />
            </div>
            <div>
              <h4 className="text-sm font-semibold text-slate-200">No Plants Registered Yet</h4>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Create your first plant record to save your custom variety, planting date, soil moisture, and pH.
              </p>
            </div>
            <button
              onClick={handleOpenAddModal}
              className="px-4 py-2 rounded-xl bg-emerald-500 text-slate-950 font-bold text-xs hover:bg-emerald-400 transition"
            >
              Register First Plant
            </button>
          </div>
        ) : (
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
            {plants.map((plant) => {
              const isSelected = selectedPlant?.id === plant.id;
              const isRice = (plant.crop_type || "").toLowerCase().includes("rice");

              return (
                <div
                  key={plant.id}
                  onClick={() => selectPlant(plant)}
                  className={`p-4 rounded-xl border text-left transition-all duration-200 cursor-pointer flex flex-col justify-between gap-3 relative group ${
                    isSelected
                      ? "bg-emerald-950/30 border-emerald-500 ring-2 ring-emerald-500/30 shadow-lg shadow-emerald-950/30"
                      : "bg-slate-950/50 border-slate-800 hover:border-slate-700 hover:bg-slate-900/60"
                  }`}
                >
                  {/* Top Bar: Icon, Crop Suite & Selection Dot */}
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{isRice ? "🌱" : "🌾"}</span>
                      <span
                        className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full ${
                          isRice
                            ? "bg-teal-500/10 text-teal-400 border border-teal-500/20"
                            : "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                        }`}
                      >
                        {plant.crop_type} Model Suite
                      </span>
                    </div>

                    <div className="flex items-center gap-1.5">
                      {isSelected && (
                        <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-md border border-emerald-500/30">
                          <Check className="w-3 h-3" /> Active
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Middle Info */}
                  <div className="space-y-1">
                    <h3 className="font-bold text-slate-100 text-sm md:text-base leading-snug truncate">
                      {plant.name}
                    </h3>
                    <p className="text-xs text-slate-400 flex items-center gap-2">
                      <span>Variety: <strong className="text-slate-200">{plant.variety || "Standard"}</strong></span>
                      <span>•</span>
                      <span>Stage: <strong className="text-slate-200">{plant.growth_stage || "Vegetative"}</strong></span>
                    </p>
                  </div>

                  {/* Badges: Field & Soil Info */}
                  <div className="pt-2 border-t border-slate-800/80 grid grid-cols-2 gap-1.5 text-[11px] text-slate-400">
                    <div className="truncate">
                      <span className="text-slate-500">Field:</span> {plant.field_name || "Plot 1"} ({plant.field_size || 1} {plant.field_size_unit || "ac"})
                    </div>
                    <div className="truncate">
                      <span className="text-slate-500">Soil:</span> {plant.soil_type || "Loam"} (pH {plant.soil_ph || 6.5})
                    </div>
                  </div>

                  {/* Actions: Edit & Delete */}
                  <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 mt-1">
                    <span className="text-[10px] text-slate-500 truncate">
                      {plant.location_name ? `📍 ${plant.location_name}` : "Tap to select for AI"}
                    </span>
                    <div className="flex items-center gap-1" onClick={(e) => e.stopPropagation()}>
                      <button
                        type="button"
                        onClick={() => handleOpenEditModal(plant)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-400 hover:bg-slate-800 transition"
                        title="Edit Plant Details"
                      >
                        <Edit3 className="w-3.5 h-3.5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => handleDeletePlant(plant.id, plant.name)}
                        className="p-1.5 rounded-lg text-slate-400 hover:text-rose-400 hover:bg-slate-800 transition"
                        title="Delete Plant"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* ======================================================== */}
      {/* SECTION 2: LOCATION MANAGEMENT & LIVE WEATHER TELEMETRY  */}
      {/* ======================================================== */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Left Column: Location Management Panel */}
        <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 flex flex-col justify-between gap-4 shadow-xl">
          <div className="space-y-3.5">
            <div className="flex items-center justify-between">
              <h2 className="font-bold text-slate-100 text-sm md:text-base flex items-center gap-2">
                <Navigation className="w-4 h-4 text-emerald-400" />
                3. Field Location Management
              </h2>
              <span className="text-[10px] uppercase font-bold text-slate-500">
                Live GPS / Search
              </span>
            </div>

            {/* GPS Trigger Button */}
            <button
              onClick={detectGPSLocation}
              disabled={locationLoading}
              className="w-full py-2.5 px-4 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 border border-emerald-500/30 text-emerald-400 font-semibold text-xs flex items-center justify-center gap-2 transition"
            >
              {locationLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Acquiring High-Precision GPS Lock...
                </>
              ) : (
                <>
                  <Compass className="w-4 h-4 text-emerald-400" />
                  Use Current GPS Location
                </>
              )}
            </button>

            {/* Search / Manual Location Bar */}
            <div className="relative" ref={searchContainerRef}>
              <label className="block text-[11px] font-medium text-slate-400 mb-1">
                Search City, District, or Town:
              </label>
              <div className="relative">
                <input
                  type="text"
                  placeholder="e.g. Madurai, Thanjavur, Ludhiana..."
                  value={searchQuery}
                  onChange={(e) => handleSearchLocations(e.target.value)}
                  onFocus={() => {
                    if (searchResults.length > 0) setShowSearchDropdown(true);
                  }}
                  className="w-full pl-9 pr-8 py-2 bg-slate-950/70 border border-slate-800 rounded-xl text-slate-200 text-xs focus:outline-none focus:border-emerald-500"
                />
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-3 top-2.5" />
                {searchLoading && (
                  <Loader2 className="w-3.5 h-3.5 text-emerald-400 animate-spin absolute right-3 top-2.5" />
                )}
              </div>

              {/* Autocomplete Dropdown */}
              {showSearchDropdown && searchResults.length > 0 && (
                <div className="absolute top-full left-0 right-0 mt-1 z-30 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl max-h-48 overflow-y-auto">
                  {searchResults.map((place, idx) => (
                    <button
                      key={idx}
                      type="button"
                      onClick={() => handleSelectSearchResult(place)}
                      className="w-full text-left px-3.5 py-2 hover:bg-slate-800/80 text-xs text-slate-200 flex items-center justify-between border-b border-slate-800/50 last:border-0"
                    >
                      <span className="truncate font-medium">{place.display_name}</span>
                      <span className="text-[10px] font-mono text-slate-500 shrink-0 pl-2">
                        {place.latitude.toFixed(2)}°, {place.longitude.toFixed(2)}°
                      </span>
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Current Active Location Display Card */}
            <div className="p-3 bg-slate-950/60 rounded-xl border border-slate-800/80 space-y-1">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                  <span className="truncate">{locationName || "Selected Field"}</span>
                </div>
                <span
                  className={`text-[9px] font-bold px-1.5 py-0.5 rounded uppercase ${
                    locationStatus === "gps"
                      ? "bg-emerald-500/20 text-emerald-400"
                      : locationStatus === "search"
                      ? "bg-sky-500/20 text-sky-400"
                      : "bg-slate-800 text-slate-400"
                  }`}
                >
                  {locationStatus === "gps" ? "GPS Locked" : locationStatus === "search" ? "Search Pick" : "Field Plot"}
                </span>
              </div>
              <p className="text-[11px] font-mono text-slate-500 pl-5">
                Lat: {coords.lat.toFixed(4)}°N, Lon: {coords.lon.toFixed(4)}°E
              </p>
              {locationError && (
                <p className="text-[11px] text-amber-400/90 pl-5 pt-1 flex items-center gap-1">
                  <AlertTriangle className="w-3 h-3 shrink-0" />
                  {locationError}
                </p>
              )}
            </div>
          </div>

          <div className="text-[11px] text-slate-500 flex items-center gap-1.5 border-t border-slate-800/80 pt-3">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            Automatic Open-Meteo & regional station alignment
          </div>
        </div>

        {/* Right 2 Columns: Live Atmospheric Telemetry Dashboard */}
        <div className="lg:col-span-2 bg-slate-900/80 p-5 rounded-2xl border border-slate-800 flex flex-col justify-between gap-4 shadow-xl">
          <div>
            <div className="flex items-center justify-between mb-3">
              <div>
                <h2 className="font-bold text-slate-100 text-sm md:text-base flex items-center gap-2">
                  <CloudSun className="w-4 h-4 text-emerald-400" />
                  4. Live Atmospheric Telemetry (Open-Meteo)
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">
                  Synchronized with active field coordinates ({coords.lat.toFixed(2)}°, {coords.lon.toFixed(2)}°)
                </p>
              </div>

              <button
                onClick={() => fetchLiveWeather(coords.lat, coords.lon, locationName)}
                disabled={weatherLoading}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium bg-slate-800/60 hover:bg-slate-800 px-2.5 py-1.5 rounded-lg border border-slate-700/60 transition"
              >
                <RefreshCw className={`w-3 h-3 ${weatherLoading ? "animate-spin" : ""}`} />
                Sync Weather
              </button>
            </div>

            {/* Weather Metrics Grid */}
            {weatherLoading ? (
              <div className="h-44 flex flex-col items-center justify-center gap-2 text-xs text-slate-400">
                <Loader2 className="w-6 h-6 animate-spin text-emerald-400" />
                Retrieving live atmospheric indices...
              </div>
            ) : weatherError ? (
              <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-900/40 text-xs text-rose-300 flex items-center justify-between">
                <span>{weatherError}</span>
                <button
                  onClick={() => fetchLiveWeather(coords.lat, coords.lon, locationName)}
                  className="font-bold underline ml-2"
                >
                  Retry
                </button>
              </div>
            ) : currentWeather ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3 text-xs">
                {/* Temperature */}
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
                    <Thermometer className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Temperature</span>
                    <span className="text-sm md:text-base font-bold text-slate-100">
                      {currentWeather.MaxT}°C
                    </span>
                    <span className="text-[10px] text-slate-500 block">Min: {currentWeather.MinT}°C</span>
                  </div>
                </div>

                {/* Morning Humidity */}
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-sky-500/10 text-sky-400">
                    <Droplets className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Morning Hum. (RH1)</span>
                    <span className="text-sm md:text-base font-bold text-slate-100">
                      {currentWeather.RH1}%
                    </span>
                    <span className="text-[10px] text-slate-500 block">Evening: {currentWeather.RH2}%</span>
                  </div>
                </div>

                {/* Rainfall */}
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400">
                    <CloudRain className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Precipitation (RF)</span>
                    <span className="text-sm md:text-base font-bold text-slate-100">
                      {currentWeather.RF} mm
                    </span>
                    <span className="text-[10px] text-slate-500 block">
                      {currentWeather.RF <= 10 ? "Low Rain" : currentWeather.RF <= 50 ? "Moderate" : "Heavy"}
                    </span>
                  </div>
                </div>

                {/* Wind Velocity */}
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-slate-500/10 text-slate-300">
                    <Wind className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Wind Velocity (WS)</span>
                    <span className="text-sm md:text-base font-bold text-slate-100">
                      {currentWeather.WS} km/h
                    </span>
                    <span className="text-[10px] text-slate-500 block">Moderate breeze</span>
                  </div>
                </div>

                {/* Sunshine Duration */}
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-yellow-500/10 text-yellow-400">
                    <Sun className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Sunshine (SSH)</span>
                    <span className="text-sm md:text-base font-bold text-slate-100">
                      {currentWeather.SSH ?? 7.0} hrs
                    </span>
                    <span className="text-[10px] text-slate-500 block">Daily canopy exposure</span>
                  </div>
                </div>

                {/* Evapotranspiration */}
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 flex items-center gap-3">
                  <div className="p-2 rounded-lg bg-indigo-500/10 text-indigo-400">
                    <Waves className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Evapotranspiration</span>
                    <span className="text-sm md:text-base font-bold text-slate-100">
                      {currentWeather.EVP ?? 4.0} mm
                    </span>
                    <span className="text-[10px] text-slate-500 block">FAO-56 reference</span>
                  </div>
                </div>

                {/* Soil Context Metric */}
                <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800 flex items-center gap-3 col-span-2">
                  <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                    <ShieldCheck className="w-5 h-5" />
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">
                      Target Plant Edaphic Balance
                    </span>
                    <span className="text-xs md:text-sm font-semibold text-slate-200">
                      {selectedPlant?.soil_type || "Loam"} • {selectedPlant?.soil_moisture || 60}% Moisture • pH {selectedPlant?.soil_ph || 6.5}
                    </span>
                    <span className="text-[10px] text-emerald-400 block mt-0.5">
                      Integrated into AI pest susceptibility analysis
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-8 text-center rounded-xl bg-slate-950/30 border border-slate-800/50 text-xs text-slate-500">
                Atmospheric data will appear once location is locked.
              </div>
            )}
          </div>

          {/* ======================================================== */}
          {/* SECTION 3: REVIEW INPUTS & RUN PREDICTION CTA           */}
          {/* ======================================================== */}
          <div className="pt-3 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
            <div className="text-xs text-slate-400">
              <span className="font-semibold text-slate-200">Ready to model: </span>
              {selectedPlant?.name || "Target Plant"} ({selectedPlant?.crop_type || "Rice"}) @ {locationName}
            </div>

            <button
              onClick={handleRunPrediction}
              disabled={analyzing || !selectedPlant || weatherLoading}
              className="w-full sm:w-auto py-3 px-6 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-xl shadow-emerald-500/20 transition-all flex items-center justify-center gap-2.5 disabled:opacity-50"
            >
              {analyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Modeling Pest Pressures & Risk Timeline...
                </>
              ) : (
                <>
                  <ScanLine className="w-4 h-4" />
                  Run AI Pest Risk Prediction
                </>
              )}
            </button>
          </div>
        </div>
      </div>

      {/* ======================================================== */}
      {/* SECTION 4: PREDICTION RESULTS DASHBOARD                  */}
      {/* ======================================================== */}
      {predictionData && (
        <div ref={resultsRef} className="space-y-6 animate-fadeIn pt-4">
          {/* Primary Top Threat Banner */}
          {predictionData.top_pest && (
            <div className="p-5 md:p-6 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950 border border-slate-800 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div className="space-y-1.5">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-emerald-400">
                  <Sparkles className="w-4 h-4" />
                  Primary Outbreak Threat Identified
                </div>
                <h2 className="text-xl md:text-2xl font-bold text-slate-100">
                  {predictionData.top_pest.pest_name_display || predictionData.top_pest.pest_name}
                </h2>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-slate-400">
                  <span>
                    Plant: <strong className="text-slate-200">{predictionData.plant?.name}</strong> ({predictionData.crop})
                  </span>
                  <span>•</span>
                  <span>
                    Field: <strong className="text-slate-200">{predictionData.plant?.field_name || "Plot 1"}</strong>
                  </span>
                  <span>•</span>
                  <span>
                    Risk Index: <strong className="text-slate-200">{predictionData.top_pest.pest_value}</strong>
                  </span>
                  <span>•</span>
                  <span>
                    Confidence: <strong className="text-slate-200">{predictionData.top_pest.confidence ? `${predictionData.top_pest.confidence}%` : "High"}</strong>
                  </span>
                  <span>•</span>
                  <span>
                    Location: <span className="text-slate-300">{predictionData.location?.display_name}</span>
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-3 w-full md:w-auto justify-end">
                <RiskBadge risk={predictionData.top_pest.risk_level} />
                <button
                  onClick={async () => {
                    try {
                      const blob = await predictService.downloadReport(predictionData.prediction_id);
                      const url = window.URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = `agrishield_report_${predictionData.prediction_id}.pdf`;
                      a.click();
                      window.URL.revokeObjectURL(url);
                      toast.success("Executive PDF report generated");
                    } catch {
                      toast.error("Report download failed");
                    }
                  }}
                  className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 flex items-center gap-1.5 transition"
                >
                  <FileDown className="w-4 h-4" />
                  PDF Report
                </button>
              </div>
            </div>
          )}

          {/* Environmental Drivers / Contributing Factors */}
          {predictionData.contributing_factors && predictionData.contributing_factors.length > 0 && (
            <div className="bg-slate-900/70 p-4 md:p-5 rounded-2xl border border-slate-800 space-y-3">
              <h3 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
                <Compass className="w-4 h-4 text-emerald-400" />
                Key Environmental Drivers & Edaphic Influences
              </h3>
              <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-3">
                {predictionData.contributing_factors.map((factor, idx) => (
                  <div key={idx} className="p-3 rounded-xl bg-slate-950/60 border border-slate-800/80 space-y-1 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-slate-200">{factor.factor}</span>
                      <span
                        className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${
                          factor.status === "High" || factor.status === "Warning"
                            ? "bg-rose-500/20 text-rose-400"
                            : factor.status === "Optimal"
                            ? "bg-emerald-500/20 text-emerald-400"
                            : "bg-slate-800 text-slate-300"
                        }`}
                      >
                        {factor.status}
                      </span>
                    </div>
                    <div className="font-mono text-emerald-400 font-bold">{factor.value}</div>
                    <p className="text-[11px] text-slate-400 leading-relaxed">{factor.impact}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Grid: Ranked Pests vs 7-Day Timeline */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Left: Ranked Multi-Pest Threat List */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-200 text-sm md:text-base flex items-center gap-2">
                  <Layers className="w-4 h-4 text-emerald-400" />
                  Comprehensive Pest Threat Ranking ({pestsRanked.length} Species)
                </h3>
                <span className="text-xs text-slate-500">Sorted by risk intensity</span>
              </div>

              <div className="space-y-2.5 max-h-[460px] overflow-y-auto pr-1 custom-scrollbar">
                {pestsRanked.map((pest, idx) => (
                  <PestRankCard
                    key={pest.pest_name}
                    pest={pest}
                    rank={idx + 1}
                    maxPestValue={pestsRanked[0]?.pest_value || 30}
                  />
                ))}
              </div>
            </div>

            {/* Right: 7-Day Forecast Risk Chart */}
            <div className="space-y-3">
              <ForecastRiskChart data={forecastRisk} />

              <div className="p-4 bg-slate-900/60 rounded-xl border border-slate-800 text-xs space-y-2 text-slate-400">
                <div className="font-semibold text-slate-200 flex items-center gap-1.5">
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400" />
                  Forecast Methodology Note
                </div>
                <p className="leading-relaxed">
                  The 7-day risk trajectory evaluates anticipated microclimate pressure by passing daily Open-Meteo
                  meteorological features into the trained multi-species regression models.
                </p>
              </div>
            </div>
          </div>

          {/* Smart Advisory Section */}
          {smartAdvisory && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="font-semibold text-slate-200 text-sm md:text-base flex items-center gap-2">
                  <ClipboardList className="w-4 h-4 text-emerald-400" />
                  Field-Level Smart Advisory & Agronomic Controls
                </h3>
                <Link
                  to={`/app/recommendation?id=${predictionData.prediction_id}`}
                  className="text-xs text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1"
                >
                  Full Advisory View <ArrowRight className="w-3 h-3" />
                </Link>
              </div>

              <SmartAdvisory advisory={smartAdvisory} />
            </div>
          )}
        </div>
      )}

      {/* Add / Edit Plant Modal */}
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
