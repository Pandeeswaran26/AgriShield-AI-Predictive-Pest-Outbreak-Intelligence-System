import React, { useEffect, useState } from "react";
import { useSearchParams, Link } from "react-router-dom";
import toast from "react-hot-toast";
import {
  Sprout,
  ShieldAlert,
  Leaf,
  TrendingDown,
  Search,
  ClipboardList,
  Sparkles,
  ArrowRight,
  FileDown,
  Droplets,
  FlaskConical,
  Bug,
  CloudSun,
  AlertTriangle,
  Clock,
  CheckCircle2,
  Calendar,
  Layers,
  Thermometer,
  Wind,
} from "lucide-react";
import RiskBadge from "../components/RiskBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import * as recommendationService from "../services/recommendationService";
import * as historyService from "../services/historyService";
import * as predictService from "../services/predictService";

export default function Recommendation() {
  const [searchParams, setSearchParams] = useSearchParams();
  const idParam = searchParams.get("id");

  const [history, setHistory] = useState([]);
  const [selectedId, setSelectedId] = useState(idParam || "");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    historyService
      .getHistory()
      .then((res) => {
        const items = res.items || [];
        setHistory(items);
        if (!selectedId && items.length > 0) {
          setSelectedId(items[0].id);
          setSearchParams({ id: items[0].id });
        }
      })
      .catch(() => {});
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    setLoading(true);
    recommendationService
      .getRecommendation(selectedId)
      .then((res) => {
        setData(res);
      })
      .catch(() => {
        toast.error("No recommendation found for that prediction");
        setData(null);
      })
      .finally(() => setLoading(false));
  }, [selectedId]);

  const handleSelect = (id) => {
    setSelectedId(id);
    setSearchParams(id ? { id } : {});
  };

  const structuredRecs = data?.structured_recommendations;
  const prioritizedActions = structuredRecs?.prioritized_actions || [];
  const irrigationPlan = structuredRecs?.irrigation_plan;
  const fertilizerPlan = structuredRecs?.fertilizer_plan;
  const weatherSprayGuidance = structuredRecs?.weather_spray_guidance;
  const decisionAssessment = data?.decision_assessment;

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* Header Banner */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold uppercase tracking-wider mb-2">
            <ClipboardList size={13} />
            AI Decision-Support & Action Center
          </div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-100 flex items-center gap-2">
            Field Treatment & Decision Plan
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Actionable agronomic decisions answering <strong>WHAT to do</strong>, <strong>WHEN to do it</strong>, and <strong>WHY</strong>.
          </p>
        </div>

        {selectedId && (
          <button
            onClick={async () => {
              try {
                const blob = await predictService.downloadReport(selectedId);
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `decision_treatment_plan_${selectedId}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
                toast.success("Executive PDF report downloaded");
              } catch {
                toast.error("Download failed");
              }
            }}
            className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 flex items-center gap-2 transition shadow-sm"
          >
            <FileDown className="w-4 h-4 text-emerald-400" /> Export Decision Report (PDF)
          </button>
        )}
      </div>

      {/* Select Assessment Dropdown */}
      <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 shadow-xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex items-center gap-3 w-full md:w-auto">
          <label className="text-xs font-semibold text-slate-300 shrink-0">Selected Assessment:</label>
          <select
            value={selectedId}
            onChange={(e) => handleSelect(e.target.value)}
            className="w-full md:w-96 px-3 py-2 bg-slate-950 border border-slate-800 rounded-xl text-xs text-slate-100 font-medium focus:outline-none focus:border-emerald-500"
          >
            {history.map((h) => (
              <option key={h.id} value={h.id}>
                #{h.id} • {h.crop} {h.plant_name ? `(${h.plant_name})` : ""} — {h.location_display || h.location} ({h.risk_level} Risk)
              </option>
            ))}
          </select>
        </div>

        <Link
          to="/app/predict"
          className="text-xs font-semibold text-emerald-400 hover:text-emerald-300 flex items-center gap-1 shrink-0"
        >
          + Run Fresh Crop Assessment <ArrowRight size={13} />
        </Link>
      </div>

      {loading ? (
        <LoadingSpinner label="Generating AI Decision Plan..." />
      ) : !data ? (
        <div className="p-12 rounded-2xl bg-slate-900/50 border border-slate-800 text-center space-y-3">
          <ClipboardList className="w-12 h-12 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-slate-200">No Assessment Record Selected</h3>
          <p className="text-xs text-slate-400">Select a prior crop assessment or run a new one from the prediction page.</p>
        </div>
      ) : (
        <div className="space-y-6 animate-fadeIn">
          {/* Top Assessment Overview Ribbon */}
          <div className="p-5 rounded-2xl bg-gradient-to-r from-slate-900 via-slate-850 to-slate-900 border border-slate-800 shadow-xl">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Crop & Variety</span>
                <p className="font-bold text-slate-100 text-sm mt-0.5">{data.crop || "Rice"}</p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Growth Phase</span>
                <p className="font-bold text-emerald-300 text-sm mt-0.5">
                  {structuredRecs?.growth_stage || data.growth_stage_info?.growth_stage || "Vegetative"}
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Crop Age</span>
                <p className="font-bold text-slate-100 text-sm mt-0.5">
                  {structuredRecs?.days_after_planting || data.growth_stage_info?.days_after_planting || 30} Days (DAP)
                </p>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Risk Evaluation</span>
                <div className="mt-0.5">
                  <RiskBadge level={data.riskLevel || "Low"} />
                </div>
              </div>
            </div>
          </div>

          {/* ───────────────────────────────────────────────────────────── */}
          {/* Section 1: Prioritized Action Stream (CRITICAL, HIGH, MEDIUM) */}
          {/* ───────────────────────────────────────────────────────────── */}
          <div className="bg-slate-900/90 p-6 rounded-2xl border border-slate-800 shadow-xl space-y-4">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-emerald-400" />
                <h3 className="text-lg font-bold text-slate-100 font-display">
                  1. Prioritized Action Stream (What • When • Why)
                </h3>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Immediate operational priorities ranked by agronomic urgency and crop stress level.
              </p>
            </div>

            {prioritizedActions.length === 0 ? (
              <div className="p-4 rounded-xl bg-slate-950/40 border border-slate-800 text-xs text-slate-400">
                Crop is in optimal condition. Maintain routine weekly crop monitoring.
              </div>
            ) : (
              <div className="space-y-3.5">
                {prioritizedActions.map((act, idx) => (
                  <div
                    key={idx}
                    className={`p-5 rounded-2xl border transition-all ${
                      act.priority === "CRITICAL"
                        ? "bg-rose-950/15 border-rose-500/40"
                        : act.priority === "HIGH"
                        ? "bg-amber-950/15 border-amber-500/40"
                        : "bg-slate-950/70 border-slate-800"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-3">
                      <div className="flex items-center gap-2.5">
                        <span
                          className={`px-2.5 py-1 rounded-lg text-xs font-extrabold uppercase tracking-wider ${
                            act.priority === "CRITICAL"
                              ? "bg-rose-500/20 text-rose-300 border border-rose-500/30"
                              : act.priority === "HIGH"
                              ? "bg-amber-500/20 text-amber-300 border border-amber-500/30"
                              : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                          }`}
                        >
                          {act.priority}
                        </span>
                        <span className="text-xs font-bold text-slate-400">[{act.domain}]</span>
                        <h4 className="text-base font-bold text-slate-100">{act.title}</h4>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs font-semibold text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                        <Clock size={13} /> {act.when}
                      </div>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4 text-xs pt-2 border-t border-slate-800/80">
                      <div>
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                          WHAT TO DO (OPERATIONAL ACTION)
                        </span>
                        <p className="text-slate-200 text-sm leading-relaxed">{act.what}</p>
                        {act.biological_options && act.biological_options.length > 0 && (
                          <div className="mt-2 text-xs text-emerald-300">
                            <strong>Biological Option:</strong> {act.biological_options[0]}
                          </div>
                        )}
                        {act.chemical_options && act.chemical_options.length > 0 && (
                          <div className="mt-1 text-xs text-amber-300">
                            <strong>Chemical Control:</strong> {act.chemical_options[0]}
                          </div>
                        )}
                      </div>
                      <div>
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">
                          WHY (AGRONOMIC & METEOROLOGICAL RATIONALE)
                        </span>
                        <p className="text-slate-400 text-xs leading-relaxed">{act.why}</p>
                        {act.safety_warning && (
                          <p className="text-[11px] text-rose-400/90 mt-2 italic">
                            ⚠️ {act.safety_warning}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* ───────────────────────────────────────────────────────────── */}
          {/* Section 2: Domain-Specific Intelligence Grid */}
          {/* ───────────────────────────────────────────────────────────── */}
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Irrigation Intelligence */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Droplets className="w-5 h-5 text-cyan-400" />
                  <h3 className="font-bold text-slate-100 text-sm">Irrigation Intelligence</h3>
                </div>
                <span className="text-xs font-bold text-cyan-400 bg-cyan-500/10 px-2.5 py-0.5 rounded-full border border-cyan-500/20">
                  {irrigationPlan?.status || "Stable"}
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Recommended Time Window:</span>
                  <span className="font-bold text-slate-200">{irrigationPlan?.window || "Next 48 hours"}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Method:</span>
                  <span className="text-slate-300">{irrigationPlan?.method || "Standard Furrow / Drip"}</span>
                </div>
                {irrigationPlan?.soil_moisture_level !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Current Soil Moisture:</span>
                    <span className="font-bold text-cyan-300">{irrigationPlan.soil_moisture_level}%</span>
                  </div>
                )}
                {irrigationPlan?.forecast_rain_sum_mm !== undefined && (
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">7-Day Rainfall Forecast:</span>
                    <span className="text-blue-300 font-semibold">{irrigationPlan.forecast_rain_sum_mm} mm</span>
                  </div>
                )}
              </div>

              <div className="text-xs text-slate-400 leading-relaxed bg-slate-950/40 p-3 rounded-xl border border-slate-800">
                <strong className="text-slate-300 block mb-0.5">Agronomic Reason:</strong>
                {irrigationPlan?.reason || "Soil moisture and weather conditions support current crop hydration."}
              </div>
            </div>

            {/* Crop Nutrition & Fertilizer */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FlaskConical className="w-5 h-5 text-emerald-400" />
                  <h3 className="font-bold text-slate-100 text-sm">Crop Nutrition & Fertilizer</h3>
                </div>
                <span className="text-xs font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-0.5 rounded-full border border-emerald-500/20">
                  Growth Stage Split
                </span>
              </div>

              {fertilizerPlan?.warning && (
                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/25 text-amber-300 text-xs flex items-start gap-2">
                  <AlertTriangle size={15} className="shrink-0 mt-0.5" />
                  <span>{fertilizerPlan.warning}</span>
                </div>
              )}

              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Application Window:</span>
                  <span className="font-bold text-slate-200">{fertilizerPlan?.when || "Next 3-5 days"}</span>
                </div>
                <div className="text-slate-200 pt-1 border-t border-slate-800">
                  <strong className="text-slate-400 block text-[10px] uppercase">Recommended Strategy:</strong>
                  <p className="mt-0.5 text-xs text-slate-300">{fertilizerPlan?.what || data.nutritionAdvisory?.strategy}</p>
                </div>
              </div>

              <div className="text-xs text-slate-400 leading-relaxed bg-slate-950/40 p-3 rounded-xl border border-slate-800">
                <strong className="text-slate-300 block mb-0.5">Nutrient Rationale:</strong>
                {fertilizerPlan?.why || "Nutrient split tailored to prevent vegetative lodging and maximize reproductive formation."}
              </div>
            </div>

            {/* Foliar Spray & Weather Timing Window */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CloudSun className="w-5 h-5 text-amber-400" />
                  <h3 className="font-bold text-slate-100 text-sm">Spray Timing & Weather Window</h3>
                </div>
                <span
                  className={`text-xs font-bold px-2.5 py-0.5 rounded-full border ${
                    weatherSprayGuidance?.spray_recommended
                      ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20"
                      : "bg-rose-500/10 text-rose-400 border border-rose-500/20"
                  }`}
                >
                  {weatherSprayGuidance?.spray_recommended ? "Spray Window Open" : "Do Not Spray Today"}
                </span>
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-slate-400">Optimal Application Hours:</span>
                  <span className="font-bold text-slate-200">{weatherSprayGuidance?.recommended_window || "Early morning (6:30 - 9:00 AM)"}</span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-center pt-1 border-t border-slate-800">
                  <div>
                    <span className="text-[10px] text-slate-400">Wind Speed</span>
                    <p className="font-bold text-slate-200">{weatherSprayGuidance?.wind_speed_kmh || 5} km/h</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400">Rainfall</span>
                    <p className="font-bold text-slate-200">{weatherSprayGuidance?.rainfall_mm || 0} mm</p>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400">Max Temp</span>
                    <p className="font-bold text-slate-200">{weatherSprayGuidance?.max_temp_c || 32}°C</p>
                  </div>
                </div>
              </div>

              {weatherSprayGuidance?.notes && (
                <div className="text-xs text-slate-400 bg-slate-950/40 p-3 rounded-xl border border-slate-800 space-y-1">
                  {weatherSprayGuidance.notes.map((note, nIdx) => (
                    <p key={nIdx}>• {note}</p>
                  ))}
                </div>
              )}
            </div>

            {/* Integrated Pest & Disease Management */}
            <div className="bg-slate-900/90 p-5 rounded-2xl border border-slate-800 shadow-xl space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bug className="w-5 h-5 text-rose-400" />
                  <h3 className="font-bold text-slate-100 text-sm">Targeted IPM & Biological Controls</h3>
                </div>
                <RiskBadge level={data.riskLevel || "Low"} />
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Biological & Cultural Options:</span>
                {data.organicAlternatives && data.organicAlternatives.length > 0 ? (
                  <ul className="space-y-1 text-emerald-300">
                    {data.organicAlternatives.map((org, oIdx) => (
                      <li key={oIdx} className="flex items-start gap-1.5">
                        <CheckCircle2 size={12} className="shrink-0 mt-0.5 text-emerald-400" />
                        <span>{org}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-400">Standard biological biocontrol agents and neem seed extract.</p>
                )}
              </div>

              <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800 space-y-2 text-xs">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Chemical Interventions (If ETL Exceeded):</span>
                {data.recommendedPesticides && data.recommendedPesticides.length > 0 ? (
                  <ul className="space-y-1 text-slate-300">
                    {data.recommendedPesticides.map((chem, cIdx) => (
                      <li key={cIdx} className="flex items-start gap-1.5">
                        <AlertTriangle size={12} className="shrink-0 mt-0.5 text-amber-400" />
                        <span>{chem}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-slate-400">Consult local agricultural extension for registered products.</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
