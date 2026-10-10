import React, { useState, useEffect } from "react";
import toast from "react-hot-toast";
import {
  Droplets,
  Thermometer,
  Wind,
  CloudRain,
  Leaf,
  BarChart2,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  Sprout,
  Sun,
  FlaskConical,
  Info,
  Clock,
  Zap,
  TriangleAlert,
  ChevronRight,
} from "lucide-react";

import { useNavigate } from "react-router-dom";
import * as irrigationService from "../services/irrigationService";

// ─── Crop options with emoji ─────────────────────────────────────────
const CROPS = [
  { value: "Rice",      label: "🌾 Rice",      days: [1, 150] },
  { value: "Wheat",     label: "🌾 Wheat",     days: [1, 130] },
  { value: "Cotton",    label: "🌿 Cotton",    days: [1, 200] },
  { value: "Maize",     label: "🌽 Maize",     days: [1, 120] },
  { value: "Soybean",   label: "🫘 Soybean",   days: [1, 140] },
  { value: "Groundnut", label: "🥜 Groundnut", days: [1, 120] },
  { value: "Sugarcane", label: "🍬 Sugarcane", days: [1, 360] },
  { value: "Tomato",    label: "🍅 Tomato",    days: [1, 100] },
  { value: "Potato",    label: "🥔 Potato",    days: [1, 100] },
];

// ─── Risk / stress color maps ─────────────────────────────────────────
const riskColors = {
  High:   { bg: "bg-red-500/15",    border: "border-red-400/40",   text: "text-red-400",   dot: "bg-red-400"   },
  Medium: { bg: "bg-amber-500/15",  border: "border-amber-400/40", text: "text-amber-400", dot: "bg-amber-400" },
  Low:    { bg: "bg-emerald-500/15",border: "border-emerald-400/40",text: "text-emerald-400",dot: "bg-emerald-400"},
};

const stressColors = {
  Severe:     "text-red-400",
  Moderate:   "text-amber-400",
  Optimal:    "text-emerald-400",
  Waterlogged:"text-blue-400",
};

// ─── Moisture bar ─────────────────────────────────────────────────────
function MoistureBar({ value, critical, optimal, max }) {
  const pct = Math.min(100, (value / 50) * 100);
  const critPct = Math.min(100, (critical / 50) * 100);
  const optPct  = Math.min(100, (optimal  / 50) * 100);
  const maxPct  = Math.min(100, (max      / 50) * 100);

  let barColor = "bg-emerald-500";
  if (value < critical)  barColor = "bg-red-500";
  else if (value < optimal) barColor = "bg-amber-500";
  else if (value > max)  barColor = "bg-blue-500";

  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-xs text-field-900/50 dark:text-mist/50">
        <span>0%</span>
        <span className="font-semibold text-field-900 dark:text-mist">{value}% VWC</span>
        <span>50%</span>
      </div>
      <div className="relative h-3 w-full rounded-full bg-field-900/10 dark:bg-mist/10 overflow-hidden">
        {/* Zone markers */}
        <div className="absolute inset-y-0 left-0 bg-red-400/20"    style={{ width: `${critPct}%` }} />
        <div className="absolute inset-y-0 bg-emerald-400/15"        style={{ left: `${critPct}%`, width: `${optPct - critPct}%` }} />
        <div className="absolute inset-y-0 bg-amber-400/15"          style={{ left: `${optPct}%`, width: `${maxPct - optPct}%` }} />
        {/* Fill */}
        <div className={`absolute inset-y-0 left-0 rounded-full transition-all duration-700 ${barColor}`}
             style={{ width: `${pct}%` }} />
        {/* Marker needle */}
        <div className="absolute inset-y-0 w-0.5 bg-white/80"
             style={{ left: `calc(${pct}% - 1px)` }} />
      </div>
      <div className="flex justify-between text-[10px] text-field-900/40 dark:text-mist/40">
        <span>Critical &lt;{critical}%</span>
        <span>Optimal {optimal}%</span>
        <span>Max {max}%</span>
      </div>
    </div>
  );
}

// ─── Gauge circle ────────────────────────────────────────────────────
function ProbabilityGauge({ probability, irrigationNeeded }) {
  const pct = Math.round(probability * 100);
  const circumference = 2 * Math.PI * 44;
  const dashoffset = circumference * (1 - probability);
  const color = irrigationNeeded
    ? pct >= 70 ? "#ef4444" : "#f59e0b"
    : "#22c55e";

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative">
        <svg width="110" height="110" viewBox="0 0 110 110">
          <circle cx="55" cy="55" r="44" fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="10" />
          <circle
            cx="55" cy="55" r="44" fill="none"
            stroke={color} strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={dashoffset}
            transform="rotate(-90 55 55)"
            style={{ transition: "stroke-dashoffset 1s ease" }}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-2xl font-bold text-field-900 dark:text-mist">{pct}%</span>
          <span className="text-[10px] text-field-900/50 dark:text-mist/50">probability</span>
        </div>
      </div>
      <p className={`mt-1 text-xs font-semibold ${irrigationNeeded ? "text-amber-400" : "text-emerald-400"}`}>
        {irrigationNeeded ? "Irrigation Needed" : "No Irrigation Required"}
      </p>
    </div>
  );
}

// ─── Input slider ─────────────────────────────────────────────────────
function SliderInput({ id, label, icon: Icon, value, onChange, min, max, step = 0.5, unit, description }) {
  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <label htmlFor={id} className="flex items-center gap-1.5 text-xs font-semibold text-field-900/70 dark:text-mist/70 uppercase tracking-wide">
          <Icon size={13} className="text-canopy" />
          {label}
        </label>
        <span className="text-sm font-bold text-canopy tabular-nums">
          {typeof value === "number" ? value.toFixed(step < 1 ? 1 : 0) : value} {unit}
        </span>
      </div>
      <input
        id={id}
        type="range"
        min={min} max={max} step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 appearance-none rounded-full bg-field-900/15 dark:bg-mist/15 accent-canopy cursor-pointer"
      />
      <div className="flex justify-between text-[10px] text-field-900/35 dark:text-mist/35">
        <span>{min}{unit}</span>
        {description && <span className="text-center">{description}</span>}
        <span>{max}{unit}</span>
      </div>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────
export default function IrrigationAI() {
  const navigate = useNavigate();
  const [crop,          setCrop]          = useState("Rice");
  const [cropDays,      setCropDays]      = useState(45);
  const [soilMoisture,  setSoilMoisture]  = useState(22.0);
  const [soilTemp,      setSoilTemp]      = useState(28.0);
  const [temperature,   setTemperature]   = useState(32.0);
  const [humidity,      setHumidity]      = useState(68.0);
  const [rainfall,      setRainfall]      = useState(0.0);
  const [loading,       setLoading]       = useState(false);
  const [result,        setResult]        = useState(null);

  const selectedCrop = CROPS.find((c) => c.value === crop);

  async function handlePredict() {
    setLoading(true);
    setResult(null);
    try {
      const res = await irrigationService.predictIrrigation({
        crop_name:        crop,
        crop_days:        cropDays,
        soil_moisture:    soilMoisture,
        soil_temperature: soilTemp,
        temperature,
        humidity,
        rainfall,
        send_email:       true,
      });
      setResult(res.data);
      toast.success("Irrigation analysis complete!");
      // Auto-log this prediction to irrigation history
      try {
        await irrigationService.logIrrigationEvent({
          plant_name:           res.data.plant_name || `${crop} Plant`,
          crop_type:            res.data.crop,
          field_position:       res.data.field_position,
          irrigation_needed:    res.data.irrigation_needed,
          irrigation_frequency: res.data.irrigation_frequency,
          irrigation_hours:     res.data.irrigation_hours,
          water_quantity:       res.data.water_quantity,
          timing_advice:        res.data.timing_advice,
          soil_moisture:        soilMoisture,
          soil_temperature:     soilTemp,
          temperature,
          humidity,
          rainfall,
          risk_level:           res.data.risk_level,
          water_stress:         res.data.water_stress,
          probability:          res.data.probability,
          dispatch_type:        "manual",
          advisory_notes:       res.data.advisory,
        });
      } catch { /* history logging is non-critical */ }
    } catch (err) {
      toast.error(err?.response?.data?.detail || "Prediction failed. Check the backend.");
    } finally {
      setLoading(false);
    }
  }

  // Auto-update crop_days range when crop changes
  useEffect(() => {
    const [min, max] = selectedCrop?.days ?? [1, 200];
    if (cropDays > max) setCropDays(max);
    if (cropDays < min) setCropDays(min);
  }, [crop]);

  const rc = result ? riskColors[result.risk_level] ?? riskColors.Medium : null;

  return (
    <div className="min-h-screen bg-mist dark:bg-field-900 p-4 md:p-6 lg:p-8">
      {/* ── Header ── */}
      <div className="mb-6 flex flex-col gap-1">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-400">
            <Droplets size={20} />
          </div>
          <div>
            <h1 className="font-display text-xl font-bold text-field-900 dark:text-mist">
              Crop Irrigation AI
            </h1>
            <p className="text-xs text-field-900/50 dark:text-mist/50">
              Precision moisture analytics & smart irrigation scheduling for optimal crop yield
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-5">
        {/* ── Left Panel: Input Form ─────────────────────────────────── */}
        <div className="lg:col-span-2 space-y-4">

          {/* View history link */}
          <button
            onClick={() => navigate("/app/irrigation-history")}
            className="w-full flex items-center justify-between rounded-xl border border-cyan-400/20 bg-cyan-500/6 px-4 py-2.5 text-xs font-semibold text-cyan-400 hover:bg-cyan-500/12 transition-colors"
          >
            <div className="flex items-center gap-2">
              <Clock size={13} />
              View Irrigation History
            </div>
            <ChevronRight size={13} />
          </button>

          {/* Crop Selector */}
          <div className="card p-4 space-y-3">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-field-900 dark:text-mist">
              <Sprout size={16} className="text-canopy" />
              Select Crop
            </h2>
            <div className="grid grid-cols-3 gap-2">
              {CROPS.map((c) => (
                <button
                  key={c.value}
                  onClick={() => setCrop(c.value)}
                  className={`rounded-xl border px-2 py-2.5 text-center text-xs font-medium transition-all ${
                    crop === c.value
                      ? "border-canopy bg-canopy/12 text-canopy font-semibold scale-[0.97]"
                      : "border-field-900/10 dark:border-mist/10 text-field-900/70 dark:text-mist/70 hover:border-canopy/40 hover:text-canopy"
                  }`}
                >
                  {c.label}
                </button>
              ))}
            </div>
          </div>

          {/* Field Inputs */}
          <div className="card p-4 space-y-5">
            <h2 className="flex items-center gap-2 text-sm font-semibold text-field-900 dark:text-mist">
              <FlaskConical size={16} className="text-cyan-400" />
              Field Conditions
            </h2>

            <SliderInput
              id="cropDays" label="Growth Days" icon={Leaf}
              value={cropDays} onChange={setCropDays}
              min={selectedCrop?.days[0] ?? 1}
              max={selectedCrop?.days[1] ?? 360}
              step={1} unit=" days"
              description="Days since planting"
            />

            <div className="h-px bg-field-900/8 dark:bg-mist/8" />

            <SliderInput
              id="soilMoisture" label="Soil Moisture" icon={Droplets}
              value={soilMoisture} onChange={setSoilMoisture}
              min={5} max={50} step={0.5} unit="% VWC"
              description="Volumetric water content"
            />

            <SliderInput
              id="soilTemp" label="Soil Temperature" icon={Thermometer}
              value={soilTemp} onChange={setSoilTemp}
              min={10} max={45} step={0.5} unit="°C"
            />

            <div className="h-px bg-field-900/8 dark:bg-mist/8" />

            <SliderInput
              id="temperature" label="Air Temperature" icon={Sun}
              value={temperature} onChange={setTemperature}
              min={10} max={50} step={0.5} unit="°C"
            />

            <SliderInput
              id="humidity" label="Humidity" icon={Wind}
              value={humidity} onChange={setHumidity}
              min={20} max={100} step={1} unit="%"
            />

            <SliderInput
              id="rainfall" label="Rainfall (24h)" icon={CloudRain}
              value={rainfall} onChange={setRainfall}
              min={0} max={200} step={1} unit=" mm"
              description="Last 24 hours"
            />
          </div>

          <button
            onClick={handlePredict}
            disabled={loading}
            className="btn-primary w-full py-3 text-sm"
          >
            {loading ? (
              <><Loader2 size={16} className="animate-spin" /> Analysing Field...</>
            ) : (
              <><Droplets size={16} /> Predict Irrigation Need</>
            )}
          </button>
        </div>

        {/* ── Right Panel: Results ───────────────────────────────────── */}
        <div className="lg:col-span-3 space-y-4">

          {/* Empty state */}
          {!result && !loading && (
            <div className="card flex h-full min-h-[340px] flex-col items-center justify-center gap-4 p-8 text-center">
              <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-500/10">
                <Droplets size={32} className="text-cyan-400" />
              </div>
              <div>
                <h3 className="font-display text-lg font-semibold text-field-900 dark:text-mist">
                  Irrigation Intelligence Ready
                </h3>
                <p className="mt-1 text-sm text-field-900/50 dark:text-mist/50 max-w-xs mx-auto">
                  Set your crop and field conditions, then run the AI analysis to get precision irrigation recommendations.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-3 mt-2 w-full max-w-sm">
                {[
                  { icon: Leaf,     label: "Multi-Crop",   sub: "Stage Specific" },
                  { icon: Droplets, label: "Soil VWC",     sub: "Root-Zone Balance" },
                  { icon: Clock,    label: "Smart Timing", sub: "Evaporation Control" },
                ].map(({ icon: Icon, label, sub }) => (
                  <div key={label} className="rounded-xl bg-field-900/4 dark:bg-mist/4 p-3 text-center">
                    <Icon size={18} className="mx-auto text-cyan-400 mb-1" />
                    <p className="text-xs font-bold text-field-900 dark:text-mist">{label}</p>
                    <p className="text-[10px] text-field-900/40 dark:text-mist/40">{sub}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="card flex min-h-[340px] flex-col items-center justify-center gap-4 p-8">
              <div className="relative">
                <div className="h-16 w-16 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin" />
                <Droplets size={22} className="absolute inset-0 m-auto text-cyan-400" />
              </div>
              <div className="text-center">
                <p className="font-semibold text-field-900 dark:text-mist">Analysing Field Conditions</p>
                <p className="text-sm text-field-900/50 dark:text-mist/50 mt-1">Analyzing root-zone moisture & weather demand…</p>
              </div>
            </div>
          )}

          {/* Results */}
          {result && !loading && (
            <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">

              {/* Decision banner */}
              <div className={`card p-4 flex items-start gap-4 border ${rc?.border} ${rc?.bg}`}>
                <div className={`mt-0.5 flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${
                  result.irrigation_needed ? "bg-amber-500/20" : "bg-emerald-500/20"
                }`}>
                  {result.irrigation_needed
                    ? <AlertTriangle size={20} className="text-amber-400" />
                    : <CheckCircle2 size={20} className="text-emerald-400" />
                  }
                </div>
                <div className="flex-1 min-w-0">
                  <p className="font-display text-base font-bold text-field-900 dark:text-mist">
                    {result.irrigation_needed
                      ? `Irrigate ${result.crop} — ${result.risk_level} Priority`
                      : `No Irrigation Required for ${result.crop}`}
                  </p>
                  <p className="text-xs text-field-900/60 dark:text-mist/60 mt-0.5">
                    Water Stress: <span className={`font-semibold ${stressColors[result.water_stress]}`}>{result.water_stress}</span>
                    &nbsp;·&nbsp;
                    Method: <span className="font-semibold text-cyan-400">{result.recommended_method}</span>
                  </p>
                </div>
                <ProbabilityGauge
                  probability={result.probability}
                  irrigationNeeded={result.irrigation_needed}
                />
              </div>

              {/* Moisture bar */}
              <div className="card p-4 space-y-3">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-field-900 dark:text-mist">
                  <Droplets size={15} className="text-cyan-400" />
                  Soil Moisture Status
                </h3>
                <MoistureBar
                  value={result.input_summary.soil_moisture}
                  critical={result.thresholds.critical}
                  optimal={result.thresholds.optimal}
                  max={result.thresholds.max}
                />
              </div>

              {/* Key metrics row */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                {[
                  { label: "Soil Moisture",    value: `${result.input_summary.soil_moisture}%`, icon: Droplets,    color: "text-cyan-400"    },
                  { label: "Air Temp",          value: `${result.input_summary.temperature}°C`, icon: Thermometer, color: "text-orange-400"  },
                  { label: "Humidity",          value: `${result.input_summary.humidity}%`,      icon: Wind,        color: "text-sky-400"     },
                  { label: "Rainfall (24h)",    value: `${result.input_summary.rainfall} mm`,   icon: CloudRain,   color: "text-blue-400"    },
                ].map(({ label, value, icon: Icon, color }) => (
                  <div key={label} className="card p-3 text-center">
                    <Icon size={18} className={`mx-auto mb-1 ${color}`} />
                    <p className="text-sm font-bold text-field-900 dark:text-mist">{value}</p>
                    <p className="text-[10px] text-field-900/50 dark:text-mist/50">{label}</p>
                  </div>
                ))}
              </div>

              {/* Water quantity */}
              <div className="card p-4 flex items-center gap-4">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-500/10 shrink-0">
                  <Zap size={18} className="text-cyan-400" />
                </div>
                <div>
                  <p className="text-xs text-field-900/50 dark:text-mist/50 font-semibold uppercase tracking-wide">
                    Recommended Water Quantity
                  </p>
                  <p className="text-base font-bold text-field-900 dark:text-mist mt-0.5">{result.water_quantity}</p>
                </div>
              </div>

              {/* Irrigation Schedule Panel */}
              <div className="card p-4 space-y-3 border border-cyan-400/15 bg-gradient-to-br from-cyan-500/4 to-emerald-500/4">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-field-900 dark:text-mist">
                  <Droplets size={15} className="text-cyan-400" />
                  Irrigation Schedule
                </h3>
                <div className="grid grid-cols-3 gap-3">
                  <div className="rounded-xl bg-field-900/5 dark:bg-mist/5 border border-field-900/8 dark:border-mist/8 p-3 text-center">
                    <p className="text-[10px] text-field-900/40 dark:text-mist/40 uppercase tracking-wide font-semibold mb-1">How Many Times</p>
                    <p className="text-sm font-bold text-cyan-400 leading-tight">{result.irrigation_frequency || "—"}</p>
                  </div>
                  <div className="rounded-xl bg-field-900/5 dark:bg-mist/5 border border-field-900/8 dark:border-mist/8 p-3 text-center">
                    <p className="text-[10px] text-field-900/40 dark:text-mist/40 uppercase tracking-wide font-semibold mb-1">Hours Needed</p>
                    <p className="text-sm font-bold text-emerald-400">{result.irrigation_hours != null ? `${result.irrigation_hours} hrs` : "—"}</p>
                  </div>
                  <div className="rounded-xl bg-field-900/5 dark:bg-mist/5 border border-field-900/8 dark:border-mist/8 p-3 text-center">
                    <p className="text-[10px] text-field-900/40 dark:text-mist/40 uppercase tracking-wide font-semibold mb-1">Field Zone</p>
                    <p className="text-xs font-bold text-amber-400 leading-tight">{result.field_position || "Primary Zone"}</p>
                  </div>
                </div>
              </div>


              {/* Advisory notes */}
              <div className="card p-4 space-y-3">
                <h3 className="flex items-center gap-2 text-sm font-semibold text-field-900 dark:text-mist">
                  <Info size={15} className="text-canopy" />
                  Field Advisory
                </h3>
                <ul className="space-y-2">
                  {result.advisory.map((line, i) => (
                    <li key={i} className="flex items-start gap-2.5">
                      <ChevronRight size={14} className="mt-0.5 shrink-0 text-canopy" />
                      <span className="text-sm text-field-900/80 dark:text-mist/80">{line}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Timing advice */}
              <div className="card p-4 flex items-start gap-3">
                <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-amber-500/12 shrink-0">
                  <Clock size={16} className="text-amber-400" />
                </div>
                <div>
                  <p className="text-xs font-semibold text-field-900/60 dark:text-mist/60 uppercase tracking-wide">
                    Spray & Irrigation Timing
                  </p>
                  <p className="text-sm text-field-900/85 dark:text-mist/85 mt-1">{result.timing_advice}</p>
                </div>
              </div>

              <div className="flex items-center justify-end gap-1.5 text-[11px] text-field-900/40 dark:text-mist/40">
                <CheckCircle2 size={12} className="text-canopy" />
                AgriShield Precision Irrigation Advisory
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
