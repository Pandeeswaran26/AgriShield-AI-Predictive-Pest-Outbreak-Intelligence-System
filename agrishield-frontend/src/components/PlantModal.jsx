import React, { useState, useEffect } from "react";
import { X, Sprout, MapPin, Layers, Sparkles, Loader2, Compass } from "lucide-react";
import toast from "react-hot-toast";

const GROWTH_STAGES = [
  "Seedling",
  "Vegetative",
  "Tillering / Squaring",
  "Flowering",
  "Boll / Grain Formation",
  "Maturity / Harvest",
];

const SOIL_TYPES = [
  "Clay Loam",
  "Black Soil (Regur)",
  "Red Sandy Loam",
  "Alluvial Soil",
  "Laterite Soil",
  "Silt Loam",
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
    field_size: 2.0,
    field_size_unit: "acres",
    soil_type: "Clay Loam",
    soil_moisture: 60.0,
    soil_ph: 6.5,
    latitude: defaultCoords?.lat || 11.0168,
    longitude: defaultCoords?.lon || 76.9558,
    location_name: defaultLocationName || "Field Station",
    notes: "",
  });

  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (initialData) {
      setFormData({
        name: initialData.name || "",
        crop_type: initialData.crop_type || "Rice",
        variety: initialData.variety || "",
        planting_date: initialData.planting_date || new Date().toISOString().split("T")[0],
        growth_stage: initialData.growth_stage || "Vegetative",
        field_name: initialData.field_name || "",
        field_size: initialData.field_size ?? 2.0,
        field_size_unit: initialData.field_size_unit || "acres",
        soil_type: initialData.soil_type || "Clay Loam",
        soil_moisture: initialData.soil_moisture ?? 60.0,
        soil_ph: initialData.soil_ph ?? 6.5,
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
        field_size: 2.5,
        field_size_unit: "acres",
        soil_type: "Clay Loam",
        soil_moisture: 60.0,
        soil_ph: 6.5,
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

  const handleApplyCurrentCoords = () => {
    if (defaultCoords) {
      handleChange("latitude", Number(defaultCoords.lat.toFixed(4)));
      handleChange("longitude", Number(defaultCoords.lon.toFixed(4)));
      if (defaultLocationName) {
        handleChange("location_name", defaultLocationName);
      }
      toast.success("Applied current telemetry coordinates");
    } else {
      toast.error("Current location telemetry not available yet");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.name.trim()) {
      toast.error("Please provide a name for this plant/crop record.");
      return;
    }

    setSubmitting(true);
    try {
      await onSave({
        ...formData,
        field_size: Number(formData.field_size) || 1.0,
        soil_moisture: Number(formData.soil_moisture) || 50.0,
        soil_ph: Number(formData.soil_ph) || 6.5,
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
                {isEditing ? "Edit Plant / Field Details" : "Register New Plant"}
              </h3>
              <p className="text-xs text-slate-400">
                Configure plant agronomy, soil parameters, and field location for AI modeling
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
          {/* Section 1: Plant Identity */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5" />
              1. Crop Identity & ML Model Mapping
            </h4>

            <div className="grid sm:grid-cols-2 gap-3.5">
              <div className="sm:col-span-2">
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Plant / Field Nickname <span className="text-rose-400">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Kaveri Sona Paddy - North Plot"
                  value={formData.name}
                  onChange={(e) => handleChange("name", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  AI Model Baseline Suite <span className="text-rose-400">*</span>
                </label>
                <select
                  value={formData.crop_type}
                  onChange={(e) => handleChange("crop_type", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  <option value="Rice">Paddy Rice (Oryza Model - Stem Borer, Blast, BPH)</option>
                  <option value="Cotton">Cotton (Gossypium Model - Bollworms, Aphids, Whitefly)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Crop Variety / Cultivar</label>
                <input
                  type="text"
                  placeholder="e.g. IR-64, RCH-2 Bt, Basmati"
                  value={formData.variety}
                  onChange={(e) => handleChange("variety", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Sowing / Planting Date</label>
                <input
                  type="date"
                  value={formData.planting_date}
                  onChange={(e) => handleChange("planting_date", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Current Phenological Stage</label>
                <select
                  value={formData.growth_stage}
                  onChange={(e) => handleChange("growth_stage", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                >
                  {GROWTH_STAGES.map((st) => (
                    <option key={st} value={st}>
                      {st}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Section 2: Field & Soil Agronomics */}
          <div className="space-y-3 pt-2 border-t border-slate-800/80">
            <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5" />
              2. Field & Edaphic (Soil) Conditions
            </h4>

            <div className="grid sm:grid-cols-3 gap-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Field Name / ID</label>
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
                  step="1"
                  value={formData.soil_moisture}
                  onChange={(e) => handleChange("soil_moisture", Number(e.target.value))}
                  className="w-full accent-emerald-500 mt-2"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">
                  Soil pH Level: <span className="text-teal-400 font-bold">{formData.soil_ph}</span>
                </label>
                <input
                  type="number"
                  step="0.1"
                  min="4.0"
                  max="9.5"
                  value={formData.soil_ph}
                  onChange={(e) => handleChange("soil_ph", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">pH Classification</label>
                <div className="py-2.5 px-3 rounded-xl bg-slate-950/40 border border-slate-800/80 text-xs font-semibold text-slate-300">
                  {formData.soil_ph < 6.0
                    ? "Acidic Soil (Low Ca/Mg)"
                    : formData.soil_ph <= 7.5
                    ? "Optimal / Neutral Soil"
                    : "Alkaline / Calcareous"}
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Geolocation Coordinates */}
          <div className="space-y-3 pt-2 border-t border-slate-800/80">
            <div className="flex items-center justify-between">
              <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5">
                <MapPin className="w-3.5 h-3.5" />
                3. Field Geolocation (For Open-Meteo Weather)
              </h4>
              <button
                type="button"
                onClick={handleApplyCurrentCoords}
                className="text-xs text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium bg-emerald-500/10 px-2.5 py-1 rounded-lg border border-emerald-500/20"
              >
                <Compass className="w-3.5 h-3.5" />
                Use Active GPS
              </button>
            </div>

            <div className="grid sm:grid-cols-3 gap-3.5">
              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Place / City Name</label>
                <input
                  type="text"
                  placeholder="e.g. Thanjavur, Tamil Nadu"
                  value={formData.location_name}
                  onChange={(e) => handleChange("location_name", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Latitude (°N)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={formData.latitude}
                  onChange={(e) => handleChange("latitude", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>

              <div>
                <label className="block text-xs font-medium text-slate-300 mb-1">Longitude (°E)</label>
                <input
                  type="number"
                  step="0.0001"
                  value={formData.longitude}
                  onChange={(e) => handleChange("longitude", e.target.value)}
                  className="w-full px-3.5 py-2.5 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-slate-300 mb-1">Field Agronomic Notes (Optional)</label>
              <textarea
                rows={2}
                placeholder="e.g. Previous crop was Green Gram. Drip fertigation scheduled alternate days."
                value={formData.notes}
                onChange={(e) => handleChange("notes", e.target.value)}
                className="w-full px-3.5 py-2 bg-slate-950/60 border border-slate-800 rounded-xl text-slate-100 text-xs focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Modal Footer */}
          <div className="flex items-center justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              disabled={submitting}
              className="px-4 py-2.5 rounded-xl border border-slate-700 text-slate-300 text-sm font-medium hover:bg-slate-800 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 transition flex items-center gap-2 disabled:opacity-50"
            >
              {submitting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : isEditing ? (
                "Save Changes"
              ) : (
                "Create Plant Record"
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
