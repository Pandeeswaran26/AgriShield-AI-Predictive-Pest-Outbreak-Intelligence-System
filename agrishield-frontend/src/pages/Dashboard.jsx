import React, { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";
import {
  ScanLine,
  ArrowRight,
  Sparkles,
  MapPin,
  CloudSun,
  Thermometer,
  CloudRain,
  Wind,
  Droplets,
  ShieldAlert,
  ClipboardList,
  Layers,
  Camera,
  Calendar,
  Sprout,
  Plus,
  Compass,
  AlertTriangle,
  CheckCircle2,
  Clock,
} from "lucide-react";
import StatCard from "../components/StatCard";
import RiskBadge from "../components/RiskBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import PlantModal from "../components/PlantModal";
import FarmMap from "../components/FarmMap";
import { useAuth } from "../context/AuthContext";
import * as dashboardService from "../services/dashboardService";
import * as weatherService from "../services/weatherService";
import * as plantService from "../services/plantService";
import toast from "react-hot-toast";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [summary, setSummary] = useState(null);
  const [fields, setFields] = useState([]);
  const [latestPrediction, setLatestPrediction] = useState(null);
  const [pestTrend, setPestTrend] = useState([]);
  const [cropAnalysis, setCropAnalysis] = useState([]);
  const [weatherSnapshot, setWeatherSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showMap, setShowMap] = useState(false);
  const [logActionField, setLogActionField] = useState(null);
  const [logActionType, setLogActionType] = useState("Irrigation");
  const [logActionNote, setLogActionNote] = useState("");
  const [loggingAction, setLoggingAction] = useState(false);
  const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

  // Plant Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = () => {
    setLoading(true);
    Promise.all([
      dashboardService.getSummary().catch(() => null),
      dashboardService.getFieldsOverview().catch(() => []),
      dashboardService.getLatestPrediction().catch(() => null),
      dashboardService.getPestTrend().catch(() => []),
      dashboardService.getCropAnalysis().catch(() => []),
    ])
      .then(([s, f, latest, p, c]) => {
        setSummary(s);
        setFields(Array.isArray(f) ? f : []);
        setLatestPrediction(latest);
        setPestTrend(p);
        setCropAnalysis(c);
      })
      .finally(() => setLoading(false));

    // Try auto-fetching live weather snapshot for local coordinates
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          weatherService
            .getWeatherForCoordinates(pos.coords.latitude, pos.coords.longitude)
            .then(setWeatherSnapshot)
            .catch(() => {});
        },
        () => {
          weatherService
            .getWeatherForCoordinates(11.0168, 76.9558)
            .then(setWeatherSnapshot)
            .catch(() => {});
        }
      );
    }
  };

  const handleCreatePlant = async (payload) => {
    try {
      await plantService.createPlant(payload);
      toast.success("New field registered successfully!");
      loadDashboardData();
    } catch {
      toast.error("Failed to register field.");
    }
  };

  const handleLogAction = async () => {
    if (!logActionField) return;
    setLoggingAction(true);
    try {
      const token = localStorage.getItem("agrishield_token");
      await fetch(`${API_BASE}/api/farmer-actions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          plant_id: logActionField.id,
          action_type: logActionType,
          description: logActionNote || `${logActionType} applied on ${logActionField.name}`,
          performed_at: new Date().toISOString(),
        }),
      });
      toast.success(`✓ Action logged: ${logActionType}`);
      setLogActionField(null);
      setLogActionNote("");
      setLogActionType("Irrigation");
    } catch {
      toast.error("Failed to log action.");
    } finally {
      setLoggingAction(false);
    }
  };

  if (loading) return <LoadingSpinner label="Loading Agricultural Decision Dashboard" />;

  const weather = weatherSnapshot?.weather;
  const loc = weatherSnapshot?.location;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Welcome Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <Sprout size={13} />
            Agricultural Decision-Support System
          </div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-100 flex items-center gap-2">
            Welcome back{user?.name ? `, ${user.name.split(" ")[0]}` : ""}
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Real-time crop surveillance, meteorological intelligence, and actionable farm decisions.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <button
            onClick={() => setIsModalOpen(true)}
            className="py-2.5 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 font-semibold text-sm transition flex items-center gap-2 shadow-sm"
          >
            <Plus size={16} className="text-emerald-400" /> Add New Field
          </button>
          <Link
            to="/app/diagnosis"
            className="py-2.5 px-4 rounded-xl border border-emerald-500/40 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 font-semibold text-sm transition flex items-center gap-2 shadow-sm"
          >
            <Camera size={16} /> Scan Plant Leaf
          </Link>
          <Link
            to="/app/predict"
            className="py-2.5 px-5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 transition flex items-center gap-2"
          >
            <ScanLine size={16} /> Run Crop Assessment
          </Link>
        </div>
      </div>

      {/* Top Banner: Regional Weather Telemetry + Quick System Telemetry */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Live Weather Telemetry Widget */}
        <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <CloudSun className="w-5 h-5 text-emerald-400" />
                <h3 className="font-semibold text-slate-200 text-sm">Live Field Telemetry</h3>
              </div>
              <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                LIVE WEATHER (OPEN-METEO)
              </span>
            </div>

            <div className="flex items-start justify-between">
              <div>
                <p className="text-3xl font-extrabold text-slate-100">
                  {weather?.MaxT ? `${Math.round(weather.MaxT)}°C` : "--°C"}
                </p>
                <p className="text-xs text-slate-400 flex items-center gap-1 mt-1">
                  <MapPin className="w-3.5 h-3.5 text-emerald-400" />
                  {loc?.name || "Field Station Location"}
                </p>
              </div>
              <div className="text-right">
                <span className="inline-block px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs font-medium text-emerald-300">
                  {weather?.RF > 5 ? "Rain Expected" : weather?.WS > 15 ? "Windy" : "Optimal Conditions"}
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-4 gap-2 pt-4 border-t border-slate-800/80 mt-4 text-center">
            <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800">
              <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
                <Thermometer size={10} className="text-rose-400" /> High/Low
              </div>
              <p className="text-xs font-bold text-slate-200 mt-0.5">
                {weather?.MaxT ? `${Math.round(weather.MaxT)}°/${Math.round(weather.MinT || 22)}°` : "—"}
              </p>
            </div>
            <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800">
              <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
                <Droplets size={10} className="text-cyan-400" /> Humidity
              </div>
              <p className="text-xs font-bold text-slate-200 mt-0.5">
                {weather?.RH1 ? `${Math.round(weather.RH1)}%` : "—"}
              </p>
            </div>
            <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800">
              <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
                <CloudRain size={10} className="text-blue-400" /> Rain
              </div>
              <p className="text-xs font-bold text-slate-200 mt-0.5">
                {weather?.RF !== undefined ? `${weather.RF} mm` : "—"}
              </p>
            </div>
            <div className="p-2 rounded-xl bg-slate-950/40 border border-slate-800">
              <div className="text-[10px] text-slate-400 flex items-center justify-center gap-1">
                <Wind size={10} className="text-teal-400" /> Wind
              </div>
              <p className="text-xs font-bold text-slate-200 mt-0.5">
                {weather?.WS ? `${weather.WS} km/h` : "—"}
              </p>
            </div>
          </div>
        </div>

        {/* Aggregate Surveillance Statistics */}
        <div className="lg:col-span-2 grid sm:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <span className="text-xs font-medium text-slate-400">Total Registered Fields</span>
              <p className="text-2xl font-bold text-slate-100 mt-1">{fields.length}</p>
            </div>
            <div className="text-xs text-emerald-400 flex items-center gap-1 mt-3">
              <Sprout size={14} /> Active Crop Portfolios
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <span className="text-xs font-medium text-slate-400">High Risk Alerts</span>
              <p className="text-2xl font-bold text-rose-400 mt-1">{summary?.highRisk || 0}</p>
            </div>
            <div className="text-xs text-rose-400/80 flex items-center gap-1 mt-3">
              <ShieldAlert size={14} /> Immediate Action Required
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-xl flex flex-col justify-between">
            <div>
              <span className="text-xs font-medium text-slate-400">Crop Health Assessments</span>
              <p className="text-2xl font-bold text-slate-100 mt-1">{summary?.totalPredictions || 0}</p>
            </div>
            <div className="text-xs text-slate-400 flex items-center gap-1 mt-3">
              <Clock size={14} /> {summary?.todayPredictions || 0} evaluated today
            </div>
          </div>
        </div>
      </div>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* Active Fields & Crops Surveillance Grid */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-lg font-bold text-slate-100 flex items-center gap-2 font-display">
              <Layers className="w-5 h-5 text-emerald-400" />
              My Fields & Crop Health Surveillance
            </h2>
            <p className="text-xs text-slate-400">
              Operational overview of your registered fields, growth stages, health risks, and recommended actions.
            </p>
          </div>
          <span className="text-xs text-slate-400 bg-slate-800 px-3 py-1 rounded-full border border-slate-700">
            {fields.length} Field{fields.length === 1 ? "" : "s"} Monitored
          </span>
        </div>

        {fields.length === 0 ? (
          <div className="p-8 rounded-2xl bg-slate-900/50 border border-slate-800 text-center space-y-3">
            <Sprout className="w-12 h-12 text-slate-600 mx-auto" />
            <h3 className="text-base font-bold text-slate-200">No Fields Registered Yet</h3>
            <p className="text-xs text-slate-400 max-w-md mx-auto">
              Add your farm plots, sowing dates, and location to activate continuous AI crop assessment and decision support.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold text-xs transition"
            >
              + Register Your First Field
            </button>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
            {fields.map((f) => (
              <div
                key={f.id}
                className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl hover:border-emerald-500/40 transition-all flex flex-col justify-between space-y-4 group"
              >
                {/* Field Header */}
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-emerald-500/10 border border-emerald-500/25 text-emerald-400 mb-1.5">
                        {f.crop_type} {f.variety ? `• ${f.variety}` : ""}
                      </span>
                      <h3 className="text-base font-bold text-slate-100 group-hover:text-emerald-300 transition">
                        {f.name}
                      </h3>
                      <p className="text-xs text-slate-400 flex items-center gap-1 mt-0.5">
                        <MapPin size={12} className="text-emerald-400 shrink-0" />
                        <span className="truncate">{f.location_name || `${f.latitude}°N, ${f.longitude}°E`}</span>
                      </p>
                    </div>
                    <RiskBadge level={f.risk_level || "Low"} />
                  </div>

                  {/* Growth Stage & DAP Tag */}
                  <div className="mt-3 p-2.5 rounded-xl bg-slate-950/50 border border-slate-800/80 space-y-1">
                    <div className="flex items-center justify-between text-xs">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Calendar size={12} className="text-emerald-400" />
                        Age: <strong>{f.days_after_planting} Days (DAP)</strong>
                      </span>
                      <span className="text-emerald-300 font-semibold text-[11px] truncate max-w-[140px]">
                        {f.growth_stage}
                      </span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800/60">
                      <span>Water Demand: <strong className="text-slate-300">{f.water_demand}</strong></span>
                      <span>Area: <strong className="text-slate-300">{f.field_size} {f.field_size_unit}</strong></span>
                    </div>
                  </div>

                  {/* Latest Diagnosis snippet if present */}
                  {f.last_diagnosis && (
                    <div className="mt-2.5 p-2 rounded-lg bg-emerald-500/5 border border-emerald-500/15 text-xs flex items-center justify-between">
                      <span className="text-slate-400 flex items-center gap-1">
                        <Camera size={12} className="text-emerald-400" /> Leaf Diagnosis:
                      </span>
                      <span className="font-semibold text-emerald-300 truncate max-w-[150px]">
                        {f.last_diagnosis.disease_name} ({Math.round(f.last_diagnosis.confidence)}%)
                      </span>
                    </div>
                  )}

                  {/* Next Prioritized Action Preview */}
                  <div className="mt-3">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 block mb-1">
                      Next Recommended Action
                    </span>
                    <p className="text-xs text-slate-300 bg-slate-950/40 p-2.5 rounded-xl border border-slate-800 line-clamp-2">
                      {f.next_action || "Routine field inspection and soil moisture check."}
                    </p>
                  </div>
                </div>

                {/* Field Action Buttons */}
                <div className="pt-3 border-t border-slate-800 flex items-center justify-between gap-2">
                  <button
                    onClick={() => navigate(`/app/predict?plantId=${f.id}`)}
                    className="flex-1 py-2 px-3 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-xs transition flex items-center justify-center gap-1.5 shadow-md shadow-emerald-500/10"
                  >
                    <ScanLine size={13} /> Run Assessment
                  </button>
                  <Link
                    to="/app/recommendations"
                    className="py-2 px-3 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 text-xs font-semibold transition flex items-center gap-1"
                  >
                    <ClipboardList size={13} /> Actions
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* ─────────────────────────────────────────────────────────────────── */}
      {/* Outbreak Intelligence & Analytics Charts */}
      {/* ─────────────────────────────────────────────────────────────────── */}
      <div className="grid lg:grid-cols-2 gap-6">
        <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <h3 className="font-bold text-slate-200 text-sm mb-1 flex items-center gap-2">
            <ShieldAlert size={16} className="text-amber-400" />
            Regional Pest Pressure Distribution
          </h3>
          <p className="text-xs text-slate-400 mb-4">Historical pest occurrences identified across surveillance rounds.</p>
          <div className="h-64">
            {pestTrend && pestTrend.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pestTrend.slice(0, 7)} margin={{ top: 10, right: 10, left: -20, bottom: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="pest" stroke="#94a3b8" fontSize={10} interval={0} angle={-15} textAnchor="end" />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                  />
                  <Bar dataKey="value" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No surveillance data recorded yet.
              </div>
            )}
          </div>
        </div>

        <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <h3 className="font-bold text-slate-200 text-sm mb-1 flex items-center gap-2">
            <Sprout size={16} className="text-emerald-400" />
            Crops Under Protection
          </h3>
          <p className="text-xs text-slate-400 mb-4">Distribution of crops monitored across your fields.</p>
          <div className="h-64">
            {cropAnalysis && cropAnalysis.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cropAnalysis} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="crop" stroke="#94a3b8" fontSize={11} />
                  <YAxis stroke="#94a3b8" fontSize={11} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "0.75rem", fontSize: "12px" }}
                  />
                  <Bar dataKey="value" fill="#06b6d4" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-xs text-slate-400">
                No crops recorded yet.
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Farm Surveillance Map */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="font-bold text-slate-200 text-sm flex items-center gap-2">
            <Compass size={16} className="text-emerald-400" />
            Farm Surveillance Map
          </h2>
          <button
            onClick={() => setShowMap(v => !v)}
            className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-300 hover:border-emerald-500/50 transition"
          >
            {showMap ? "Hide Map" : "Show Map"}
          </button>
        </div>
        {showMap && <FarmMap plants={fields} onFieldClick={(f) => setLogActionField(f)} />}
      </div>

      {/* Log Action Modal */}
      {logActionField && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={() => setLogActionField(null)}
        >
          <div
            className="bg-slate-900 border border-slate-700 rounded-2xl p-6 w-full max-w-sm shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            <h3 className="font-bold text-slate-100 text-base mb-1">Log Action Taken</h3>
            <p className="text-xs text-slate-400 mb-5">Record what you applied on <strong className="text-emerald-400">{logActionField.name}</strong></p>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Action Type</label>
                <select
                  value={logActionType}
                  onChange={e => setLogActionType(e.target.value)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2.5 text-sm text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  {["Irrigation","Fertilizer","Chemical Spray","Biological Treatment","Scouting","No Action","Other"].map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1.5">Notes (optional)</label>
                <textarea
                  value={logActionNote}
                  onChange={e => setLogActionNote(e.target.value)}
                  placeholder="e.g. Applied Chlorpyrifos 2L/acre at 6am..."
                  rows={3}
                  className="w-full bg-slate-800 border border-slate-700 rounded-xl px-3 py-2 text-sm text-slate-200 resize-none focus:outline-none focus:border-emerald-500 placeholder-slate-600"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-5">
              <button
                onClick={() => setLogActionField(null)}
                className="flex-1 py-2.5 rounded-xl bg-slate-800 border border-slate-700 text-slate-300 text-sm font-semibold hover:bg-slate-700 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleLogAction}
                disabled={loggingAction}
                className="flex-1 py-2.5 rounded-xl bg-emerald-500 hover:bg-emerald-400 disabled:opacity-60 text-slate-950 text-sm font-bold transition"
              >
                {loggingAction ? "Saving…" : "✓ Log Action"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Modal for adding plants */}
      <PlantModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleCreatePlant}
        defaultCoords={weatherSnapshot?.location ? { lat: weatherSnapshot.location.latitude, lon: weatherSnapshot.location.longitude } : null}
        defaultLocationName={weatherSnapshot?.location?.name || ""}
      />
    </div>
  );
}
