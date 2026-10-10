import React, { useState, useEffect } from "react";
import { X, Sprout, MapPin, Layers, Sparkles, Loader2, Compass, Calendar, Droplets, FlaskConical, Navigation, Bell, Clock, Timer } from "lucide-react";
import toast from "react-hot-toast";

const CROPS_LIST = [
  { value: "Rice", label: "Paddy Rice (Oryza - Stem Borer, Blast, BPH)", group: "Cereal / Field" },
  { value: "Cotton", label: "Cotton (Gossypium - Bollworms, Aphids, Whitefly)", group: "Cash Crop" },
  { value: "Tomato", label: "Tomato (Solanum - Blight, Bacterial Spot, Mosaic)", group: "Horticulture" },
  { value: "Potato", label: "Potato (Early & Late Blight, Tuber Health)", group: "Tuber" },
  { value: "Corn", label: "Corn / Maize (Common Rust, Northern Blight)", group: "Cereal" },
  { value: "Wheat", label: "Wheat (Rust, Powdery Mildew, Head Blight)", group: "Cereal" },
  { value: "Apple", label: "Apple (Apple Scab, Black Rot, Cedar Rust)", group: "Orchard" },
  { value: "Grape", label: "Grape (Black Rot, Esca, Leaf Blight)", group: "Vineyard" },
  { value: "Bell Pepper", label: "Bell Pepper / Capsicum (Bacterial Spot)", group: "Horticulture" },
];

const SOIL_TYPES = [
  "Clay Loam",
  "Black Soil (Regur)",
  "Red Sandy Loam",
  "Alluvial Soil",
  "Laterite Soil",
  "Silt Loam",
];

const IRRIGATION_METHODS = [
  "Drip Irrigation",
  "Sprinkler System",
  "Flood / Furrow",
  "Basin / Border",
  "Rainfed (Unirrigated)",
];

const IRRIGATION_FREQUENCIES = [
  "1 time daily (Morning)",
  "2 times daily (Morning & Evening)",
  "Every 2 days",
  "Every 3 days",
  "Weekly (As needed)",
];

export default function PlantModal({
  isOpen,
  onClose,
  onSave,
  initialData = null,
  defaultCoords = null,
  defaultLocationName = "",
}) {
  const isEditing = Boolean(initialData?.id);

  const [formData, setFormData] = useState({
    name: "",
    crop_type: "Rice",
    variety: "",
    planting_date: new Date().toISOString().split("T")[0],
    growth_stage: "Vegetative",
    field_name: "",
    field_position: "",
    field_size: 2.0,
    field_size_unit: "acres",
    irrigation_method: "Drip Irrigation",
    irrigation_frequency: "2 times daily (Morning & Evening)",
    irrigation_hours: 2.0,
    auto_irrigation_alerts: true,
    soil_type: "Clay Loam",
    soil_moisture: 60.0,
    soil_ph: 6.5,
    soil_n: "",
    soil_p: "",
    soil_k: "",
    latitude: defaultCoords?.lat || 11.0168,
    longitude: defaultCoords?.lon || 76.9558,
    location_name: defaultLocationName || "Field Station",
    notes: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [gpsDetecting, setGpsDetecting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || "",
        crop_type: initialData.crop_type || "Rice",
        variety: initialData.variety || "",
        planting_date: initialData.planting_date || new Date().toISOString().split("T")[0],
        growth_stage: initialData.growth_stage || "Vegetative",
        field_name: initialData.field_name || "",
        field_position: initialData.field_position || "",
        field_size: initialData.field_size ?? 2.0,
        field_size_unit: initialData.field_size_unit || "acres",
        irrigation_method: initialData.irrigation_method || "Drip Irrigation",
        irrigation_frequency: initialData.irrigation_frequency || "2 times daily (Morning & Evening)",
        irrigation_hours: initialData.irrigation_hours ?? 2.0,
        auto_irrigation_alerts: initialData.auto_irrigation_alerts ?? true,
        soil_type: initialData.soil_type || "Clay Loam",
        soil_moisture: initialData.soil_moisture ?? 60.0,
        soil_ph: initialData.soil_ph ?? 6.5,
        soil_n: initialData.soil_n ?? "",
        soil_p: initialData.soil_p ?? "",
        soil_k: initialData.soil_k ?? "",
        latitude: initialData.latitude ?? defaultCoords?.lat ?? 11.0168,
        longitude: initialData.longitude ?? defaultCoords?.lon ?? 76.9558,
        location_name: initialData.location_name || defaultLocationName || "",
        notes: initialData.notes || "",
      });
    } else {
      setFormData({
        name: "",
        crop_type: "Rice",
        variety: "",
        planting_date: new Date().toISOString().split("T")[0],
        growth_stage: "Vegetative",
        field_name: "",
        field_position: "",
        field_size: 2.5,
        field_size_unit: "acres",
        irrigation_method: "Drip Irrigation",
        irrigation_frequency: "2 times daily (Morning & Evening)",
        irrigation_hours: 2.0,
        auto_irrigation_alerts: true,
        soil_type: "Clay Loam",
        soil_moisture: 60.0,
        soil_ph: 6.5,
        soil_n: "",
        soil_p: "",
        soil_k: "",
        latitude: defaultCoords?.lat ?? 11.0168,
        longitude: defaultCoords?.lon ?? 76.9558,
        location_name: defaultLocationName || "",
        notes: "",
      });
    }
  }, [initialData, defaultCoords, defaultLocationName, isOpen]);

  if (!isOpen) return null;

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  // Calculate live DAP from planting date
  const calculateDAP = () => {
    if (!formData.planting_date) return null;
    try {
      const p = new Date(formData.planting_date);
      const today = new Date();
      const diff = Math.floor((today - p) / (1000 * 60 * 60 * 24));
      return Math.max(0, diff);
    } catch {
      return null;
    }
  };
  const liveDAP = calculateDAP();

  const handleApplyCurrentCoords = () => {
    if (defaultCoords) {
      handleChange("latitude", Number(defaultCoords.lat.toFixed(4)));
      handleChange("longitude", Number(defaultCoords.lon.toFixed(4)));
      if (defaultLocationName) {
        handleChange("location_name", defaultLocationName);
      }
      toast.success("Applied active location coordinates");
    } else {
      toast.error("Current location telemetry not available yet");
    }
  };

  const handleDetectGPS = () => {
    if (!navigator.geolocation) {
      toast.error("GPS / Geolocation is not supported by your browser.");
      return;
    }
    setGpsDetecting(true);
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        const lat = Number(pos.coords.latitude.toFixed(4));
        const lon = Number(pos.coords.longitude.toFixed(4));
        handleChange("latitude", lat);
        handleChange("longitude", lon);
        // Try to reverse-geocode using Nominatim
        try {
          const res = await fetch(
            `https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`
          );
          if (res.ok) {
            const data = await res.json();
            const addr = data.address || {};
            const name = [
              addr.village || addr.town || addr.city || addr.county || "",
              addr.state || "",
            ]
              .filter(Boolean)
              .join(", ");
            if (name) handleChange("location_name", name);
          }
        } catch {}
        toast.success(`GPS Location Detected: ${lat}°N, ${lon}°E`);
        setGpsDetecting(false);
      },
      (err) => {
        setGpsDetecting(false);
        if (err.code === 1) {
          toast.error("GPS permission denied. Enable location access and try again.");
        } else {
          toast.error("GPS detection failed. Please enter coordinates manually.");
        }
      },
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Please provide a name for this plant/field record.");
      return;
    }

    setSubmitting(true);
    try {
      await onSave({
        ...formData,
        field_size: Number(formData.field_size) || 1.0,
        irrigation_hours: formData.irrigation_hours !== "" ? Number(formData.irrigation_hours) : 2.0,
        auto_irrigation_alerts: Boolean(formData.auto_irrigation_alerts),
        soil_moisture: Number(formData.soil_moisture) || 50.0,
        soil_ph: Number(formData.soil_ph) || 6.5,
        soil_n: formData.soil_n !== "" ? Number(formData.soil_n) : null,
        soil_p: formData.soil_p !== "" ? Number(formData.soil_p) : null,
        soil_k: formData.soil_k !== "" ? Number(formData.soil_k) : null,
        latitude: Number(formData.latitude) || 11.0168,
        longitude: Number(formData.longitude) || 76.9558,
      });
      onClose();
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Failed to save plant record");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fadeIn">
      <div className="relative w-full max-w-2xl max-h-[92vh] flex flex-col bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl overflow-hidden">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-5 border-b border-slate-800 bg-slate-900/90">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
              <Sprout className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-bold text-slate-100 text-lg">
                {isEditing ? "Edit Plant / Field Details" : "Register New Plant / Field"}
              </h3>
              <p className="text-xs text-slate-400">
                Configure plant agronomy, planting date, soil parameters, and field coordinates
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body: Form */}
        <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-5 space-y-5 custom-scrollbar">
          {/* Section 1: Plant Identity & Growth Schedule */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              1. Crop Identity & Planting Date
            </h4>

            <div className="grid sm:grid-cols-2 gap-3.5">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Plant / Field Nickname <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Kaveri Sona Paddy - North Plot A"
                  value={formData.name}
                  onChange={(e) => handleChange("name", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Crop Type <span className="text-rose-400">*</span>
                </label>
                <select
                  value={formData.crop_type}
                  onChange={(e) => handleChange("crop_type", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  {CROPS_LIST.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Crop Variety / Cultivar</label>
                <input
                  type="text"
                  placeholder="e.g. IR-64, RCH-2 Bt, Roma, Basmati"
                  value={formData.variety}
                  onChange={(e) => handleChange("variety", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Sowing / Planting Date <span className="text-emerald-400 font-normal">({liveDAP !== null ? `${liveDAP} days ago` : "—"})</span>
                </label>
                <input
                  type="date"
                  value={formData.planting_date}
                  onChange={(e) => handleChange("planting_date", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Growth Stage <span className="text-xs text-slate-400 font-normal">(Auto-calculated)</span>
                </label>
                <input
                  type="text"
                  placeholder="e.g. Tillering, Flowering, Vegetative"
                  value={formData.growth_stage}
                  onChange={(e) => handleChange("growth_stage", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            {liveDAP !== null && (
              <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-xs text-emerald-300 flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <Calendar size={14} /> Calculated Crop Age: <strong>{liveDAP} Days After Planting (DAP)</strong>
                </span>
                <span className="text-xs text-slate-400">Stage: {formData.growth_stage || "Dynamic"}</span>
              </div>
            )}
          </div>

          {/* Section 2: Field & Soil Agronomics */}
          <div className="space-y-3 pt-2 border-t border-slate-800/80">
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              2. Field, Soil & Irrigation Method
            </h4>

            <div className="grid sm:grid-cols-3 gap-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Field Name / Plot ID</label>
                <input
                  type="text"
                  placeholder="e.g. East Parcel #2"
                  value={formData.field_name}
                  onChange={(e) => handleChange("field_name", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Field Area</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    step="0.1"
                    min="0.1"
                    value={formData.field_size}
                    onChange={(e) => handleChange("field_size", e.target.value)}
                    className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                  />
                  <select
                    value={formData.field_size_unit}
                    onChange={(e) => handleChange("field_size_unit", e.target.value)}
                    className="px-2.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-emerald-500"
                  >
                    <option value="acres">Acres</option>
                    <option value="ha">Hectares</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Irrigation Method</label>
                <select
                  value={formData.irrigation_method}
                  onChange={(e) => handleChange("irrigation_method", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  {IRRIGATION_METHODS.map((im) => (
                    <option key={im} value={im}>
                      {im}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Soil Classification</label>
                <select
                  value={formData.soil_type}
                  onChange={(e) => handleChange("soil_type", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  {SOIL_TYPES.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Soil Moisture: <span className="text-emerald-400 font-bold">{formData.soil_moisture}%</span>
                </label>
                <input
                  type="range"
                  min="10"
                  max="100"
                  step="5"
                  value={formData.soil_moisture}
                  onChange={(e) => handleChange("soil_moisture", Number(e.target.value))}
                  className="w-full accent-emerald-500 mt-2 cursor-pointer"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Soil pH (0–14)</label>
                <input
                  type="number"
                  step="0.1"
                  min="3.0"
                  max="10.0"
                  value={formData.soil_ph}
                  onChange={(e) => handleChange("soil_ph", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            {/* Irrigation Schedule, Position & Alerts */}
            <div className="p-3.5 rounded-xl bg-cyan-950/20 border border-cyan-800/40 space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-cyan-300 flex items-center gap-1.5">
                  <Droplets size={14} className="text-cyan-400" /> Water Irrigation Schedule & Email Alert
                </span>
                <span className="text-[11px] text-slate-400">Automated morning/evening dispatch</span>
              </div>

              <div className="grid sm:grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1 flex items-center gap-1">
                    <MapPin size={12} className="text-cyan-400" /> Field Position / Zone
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. Zone A - Row 3, North Plot"
                    value={formData.field_position}
                    onChange={(e) => handleChange("field_position", e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500 placeholder-slate-600"
                  />
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1 flex items-center gap-1">
                    <Clock size={12} className="text-cyan-400" /> How Many Times Needed
                  </label>
                  <select
                    value={formData.irrigation_frequency}
                    onChange={(e) => handleChange("irrigation_frequency", e.target.value)}
                    className="w-full px-3 py-2 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                  >
                    {IRRIGATION_FREQUENCIES.map((f) => (
                      <option key={f} value={f}>{f}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-medium text-slate-300 mb-1 flex items-center gap-1">
                    <Timer size={12} className="text-cyan-400" /> Hours Needed (Runtime)
                  </label>
                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      step="0.5"
                      min="0.5"
                      max="24"
                      value={formData.irrigation_hours}
                      onChange={(e) => handleChange("irrigation_hours", Number(e.target.value))}
                      className="w-full px-3 py-2 bg-slate-950/70 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-cyan-500"
                    />
                    <span className="text-xs text-slate-400 font-medium">hrs</span>
                  </div>
                </div>
              </div>

              <label className="flex items-center gap-2.5 pt-1 text-xs text-slate-200 cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={formData.auto_irrigation_alerts}
                  onChange={(e) => handleChange("auto_irrigation_alerts", e.target.checked)}
                  className="rounded border-slate-700 bg-slate-900 text-cyan-500 focus:ring-0 focus:ring-offset-0 h-4 w-4"
                />
                <span className="flex items-center gap-1.5">
                  <Bell size={13} className="text-amber-400" />
                  <span><strong>Send automated email alert</strong> when water is needed for this plant (Morning 6:00 AM & Evening 6:00 PM)</span>
                </span>
              </label>
            </div>

            {/* Optional Soil NPK */}
            <div className="mt-2 p-3.5 rounded-xl bg-slate-950/40 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-300 flex items-center gap-1.5">
                  <FlaskConical size={14} className="text-amber-400" /> Optional Soil Test Nutrients (N-P-K)
                </span>
                <span className="text-xs text-slate-400">Leave blank if no lab test available</span>
              </div>
              <div className="grid grid-cols-3 gap-3">
                <div>
                  <label className="block text-xs text-slate-400 mb-0.5">Nitrogen (kg/ha)</label>
                  <input
                    type="number"
                    placeholder="e.g. 140"
                    value={formData.soil_n}
                    onChange={(e) => handleChange("soil_n", e.target.value)}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-0.5">Phosphorus (kg/ha)</label>
                  <input
                    type="number"
                    placeholder="e.g. 45"
                    value={formData.soil_p}
                    onChange={(e) => handleChange("soil_p", e.target.value)}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
                <div>
                  <label className="block text-xs text-slate-400 mb-0.5">Potassium (kg/ha)</label>
                  <input
                    type="number"
                    placeholder="e.g. 180"
                    value={formData.soil_k}
                    onChange={(e) => handleChange("soil_k", e.target.value)}
                    className="w-full px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-xs text-slate-100 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Geolocation Coordinates */}
          <div className="space-y-3 pt-2 border-t border-slate-800/80">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5" />
                3. Field Geolocation (For Live Weather & Risk)
              </h4>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={handleDetectGPS}
                  disabled={gpsDetecting}
                  className="text-xs font-medium text-emerald-400 hover:text-emerald-300 flex items-center gap-1 transition disabled:opacity-50"
                >
                  {gpsDetecting ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <Navigation className="w-3.5 h-3.5" />
                  )}
                  {gpsDetecting ? "Detecting..." : "Detect GPS"}
                </button>
                {defaultCoords && (
                  <button
                    type="button"
                    onClick={handleApplyCurrentCoords}
                    className="text-xs font-medium text-slate-400 hover:text-slate-200 flex items-center gap-1 transition"
                  >
                    <Compass className="w-3.5 h-3.5" /> Use Page Location
                  </button>
                )}
              </div>
            </div>

            <div className="grid sm:grid-cols-3 gap-3.5">
              <div className="sm:col-span-3">
                <label className="block text-xs font-medium text-slate-300 mb-1">Location Label</label>
                <input
                  type="text"
                  placeholder="e.g. Thanjavur, Tamil Nadu"
                  value={formData.location_name}
                  onChange={(e) => handleChange("location_name", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Latitude</label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={formData.latitude}
                  onChange={(e) => handleChange("latitude", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Longitude</label>
                <input
                  type="number"
                  step="0.0001"
                  required
                  value={formData.longitude}
                  onChange={(e) => handleChange("longitude", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div className="flex items-end">
                <span className="text-xs text-slate-400 pb-2.5">
                  Live Open-Meteo weather will be fetched automatically.
                </span>
              </div>
            </div>
          </div>

          {/* Section 4: Agronomic Notes */}
          <div className="space-y-2 pt-2 border-t border-slate-800/80">
            <label className="block text-xs font-medium text-slate-300">Farmer Agronomic Field Notes</label>
            <textarea
              rows={2}
              placeholder="e.g. Drip line installed; treated seeds used; neighboring plots reported whitefly."
              value={formData.notes}
              onChange={(e) => handleChange("notes", e.target.value)}
              className="w-full px-3.5 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500 custom-scrollbar"
            />
          </div>

          {/* Modal Footer */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-sm font-medium text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 transition flex items-center gap-2"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                </>
              ) : isEditing ? (
                "Save Changes"
              ) : (
                "Save Plant / Field"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
