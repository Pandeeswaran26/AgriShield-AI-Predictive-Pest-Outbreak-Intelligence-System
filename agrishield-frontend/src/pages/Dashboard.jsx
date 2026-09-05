import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
} from "lucide-react";
import StatCard from "../components/StatCard";
import RiskBadge from "../components/RiskBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import ForecastRiskChart from "../components/ForecastRiskChart";
import { useAuth } from "../context/AuthContext";
import * as dashboardService from "../services/dashboardService";
import * as weatherService from "../services/weatherService";

export default function Dashboard() {
  const { user } = useAuth();
  const [summary, setSummary] = useState(null);
  const [latestPrediction, setLatestPrediction] = useState(null);
  const [pestTrend, setPestTrend] = useState([]);
  const [cropAnalysis, setCropAnalysis] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [weatherSnapshot, setWeatherSnapshot] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      dashboardService.getSummary(),
      dashboardService.getLatestPrediction().catch(() => null),
      dashboardService.getPestTrend(),
      dashboardService.getCropAnalysis(),
      dashboardService.getMonthlyPredictions(),
    ])
      .then(([s, latest, p, c, m]) => {
        setSummary(s);
        setLatestPrediction(latest);
        setPestTrend(p);
        setCropAnalysis(c);
        setMonthly(m);
      })
      .finally(() => setLoading(false));

    // Try auto-fetching weather snapshot for dashboard widget
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          weatherService
            .getWeatherForCoordinates(pos.coords.latitude, pos.coords.longitude)
            .then(setWeatherSnapshot)
            .catch(() => {});
        },
        () => {
          // Default station fallback
          weatherService
            .getWeatherForCoordinates(11.0168, 76.9558)
            .then(setWeatherSnapshot)
            .catch(() => {});
        }
      );
    }
  }, []);

  if (loading) return <LoadingSpinner label="Loading dashboard" />;

  const weather = weatherSnapshot?.weather;
  const loc = weatherSnapshot?.location;

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      {/* Welcome Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-100 flex items-center gap-2">
            <Sparkles className="w-6 h-6 text-emerald-400" />
            Welcome back{user?.name ? `, ${user.name.split(" ")[0]}` : ""}
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Real-time agricultural surveillance & pest intelligence overview.
          </p>
        </div>
        <Link
          to="/app/predict"
          className="py-2.5 px-5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 hover:from-emerald-400 hover:to-teal-500 text-slate-950 font-bold text-sm shadow-lg shadow-emerald-500/20 transition-all flex items-center gap-2"
        >
          <ScanLine size={17} /> Analyze Field Outbreak
        </Link>
      </div>

      {/* Top Banner: Weather Telemetry Widget + Latest Outbreak Card */}
      <div className="grid lg:grid-cols-3 gap-5">
        {/* Weather Telemetry Widget */}
        <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <CloudSun className="w-4 h-4 text-emerald-400" />
                Live Atmospheric Telemetry
              </span>
              <span className="text-[11px] text-emerald-400 font-mono">Open-Meteo API</span>
            </div>

            <div className="flex items-center gap-2 text-sm font-semibold text-slate-200 mb-3">
              <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
              <span className="truncate">{loc?.name || "Local Research Center"}</span>
            </div>

            {weather ? (
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80 flex items-center gap-2 text-slate-300">
                  <Thermometer className="w-4 h-4 text-amber-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-500 block">Temperature</span>
                    <span className="font-bold">{weather.MaxT}°C</span>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80 flex items-center gap-2 text-slate-300">
                  <Droplets className="w-4 h-4 text-sky-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-500 block">Humidity</span>
                    <span className="font-bold">{weather.RH1}%</span>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80 flex items-center gap-2 text-slate-300">
                  <CloudRain className="w-4 h-4 text-teal-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-500 block">Precipitation</span>
                    <span className="font-bold">{weather.RF} mm</span>
                  </div>
                </div>

                <div className="bg-slate-950/60 p-2.5 rounded-xl border border-slate-800/80 flex items-center gap-2 text-slate-300">
                  <Wind className="w-4 h-4 text-slate-400 shrink-0" />
                  <div>
                    <span className="text-[10px] text-slate-500 block">Wind Velocity</span>
                    <span className="font-bold">{weather.WS} km/h</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="p-4 text-center text-xs text-slate-500">Syncing live climate data...</div>
            )}
          </div>

          <p className="text-[11px] text-slate-500 pt-3 border-t border-slate-800/80 mt-3">
            Real-time feed drives pest incubation likelihood index
          </p>
        </div>

        {/* Latest Prediction Outbreak Card */}
        <div className="lg:col-span-2 bg-gradient-to-br from-slate-900 via-slate-900/90 to-slate-950 p-5 rounded-2xl border border-slate-800 shadow-xl flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
                <ShieldAlert className="w-4 h-4 text-amber-400" />
                Latest Field Surveillance Status
              </span>
              {latestPrediction && <RiskBadge risk={latestPrediction.risk_level} />}
            </div>

            {latestPrediction ? (
              <div className="space-y-2.5 mt-2">
                <div className="flex flex-col sm:flex-row sm:items-baseline justify-between gap-1">
                  <h3 className="text-lg md:text-xl font-bold text-slate-100">
                    {latestPrediction.crop}: {latestPrediction.pest_name}
                  </h3>
                  <span className="text-xs text-slate-400">
                    Severity Index: <strong className="text-slate-200">{latestPrediction.pest_value}</strong>
                  </span>
                </div>

                <p className="text-xs text-slate-400 leading-relaxed">
                  Surveillance recorded for <strong>{latestPrediction.location_display}</strong>.
                  {latestPrediction.pests_ranked?.length > 1 && (
                    <span>
                      {" "}
                      Evaluated across <strong>{latestPrediction.pests_ranked.length}</strong> co-occurring
                      pest species.
                    </span>
                  )}
                </p>

                {/* Micro tags */}
                <div className="flex flex-wrap gap-2 pt-1">
                  <span className="px-2.5 py-1 rounded-md bg-slate-950 border border-slate-800 text-[11px] text-slate-300">
                    Crop: <strong>{latestPrediction.crop}</strong>
                  </span>
                  <span className="px-2.5 py-1 rounded-md bg-slate-950 border border-slate-800 text-[11px] text-slate-300">
                    Station: <strong>{latestPrediction.location}</strong>
                  </span>
                  {latestPrediction.confidence && (
                    <span className="px-2.5 py-1 rounded-md bg-emerald-950/40 border border-emerald-500/30 text-[11px] text-emerald-300">
                      Model Confidence: <strong>{latestPrediction.confidence}%</strong>
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <div className="py-6 text-center text-xs text-slate-500">
                No recent field prediction recorded. Click "Analyze Field Outbreak" to begin.
              </div>
            )}
          </div>

          <div className="flex items-center justify-between pt-3 border-t border-slate-800/80 mt-3">
            <Link
              to="/app/history"
              className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1"
            >
              Surveillance Log History →
            </Link>
            {latestPrediction && (
              <Link
                to={`/app/recommendation?id=${latestPrediction.id}`}
                className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
              >
                <ClipboardList className="w-3.5 h-3.5" /> View Active Treatment Plan
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* 7-Day Forecast Risk Chart if available on latest prediction */}
      {latestPrediction?.forecast_risk?.length > 0 && (
        <div>
          <ForecastRiskChart data={latestPrediction.forecast_risk} />
        </div>
      )}

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 gap-4 md:grid-cols-5">
        <StatCard label="Total Predictions" value={summary?.totalPredictions ?? 0} accent="sky" />
        <StatCard label="High Risk Outbreaks" value={summary?.highRisk ?? 0} accent="alert" />
        <StatCard label="Medium Risk Alerts" value={summary?.mediumRisk ?? 0} accent="clay" />
        <StatCard label="Low Risk Baselines" value={summary?.lowRisk ?? 0} accent="canopy" />
        <StatCard label="Today's Analyses" value={summary?.todayPredictions ?? 0} accent="sky" />
      </div>

      {/* Analytical Charts */}
      <div className="grid gap-5 lg:grid-cols-2">
        <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <h2 className="font-semibold text-slate-200 text-sm md:text-base flex items-center gap-2 mb-4">
            <Layers className="w-4 h-4 text-emerald-400" />
            Historical Predictions by Pest Species
          </h2>
          <div className="h-64">
            {pestTrend.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pestTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="pest" stroke="#64748b" fontSize={10} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
                  />
                  <Bar dataKey="value" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState text="Pest frequency distribution will populate as predictions are logged." />
            )}
          </div>
        </div>

        <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-xl">
          <h2 className="font-semibold text-slate-200 text-sm md:text-base flex items-center gap-2 mb-4">
            <Layers className="w-4 h-4 text-teal-400" />
            Predictions by Crop Distribution
          </h2>
          <div className="h-64">
            {cropAnalysis.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cropAnalysis}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="crop" stroke="#64748b" fontSize={11} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
                  <Tooltip
                    contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
                  />
                  <Bar dataKey="value" fill="#0d9488" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <EmptyState text="Crop distribution will populate as predictions are logged." />
            )}
          </div>
        </div>
      </div>

      {/* Monthly Activity */}
      <div className="bg-slate-900/80 p-5 rounded-2xl border border-slate-800 shadow-xl">
        <h2 className="font-semibold text-slate-200 text-sm md:text-base mb-4">
          Monthly Outbreak Prediction Velocity
        </h2>
        <div className="h-56">
          {monthly.length ? (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={monthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="month" stroke="#64748b" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748b" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0f172a", borderColor: "#334155", borderRadius: "8px" }}
                />
                <Bar dataKey="count" fill="#3b82f6" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState text="Monthly trend velocity will plot over time." />
          )}
        </div>
      </div>
    </div>
  );
}

function EmptyState({ text }) {
  return (
    <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-xs text-slate-500">
      <p>{text}</p>
      <Link to="/app/predict" className="inline-flex items-center gap-1 text-emerald-400 hover:underline font-semibold">
        Launch First Prediction <ArrowRight size={13} />
      </Link>
    </div>
  );
}
