import React, { useState, useEffect, useCallback } from "react";
import toast from "react-hot-toast";
import {
  Droplets,
  Clock,
  Calendar,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  Loader2,
  Trash2,
  RefreshCw,
  Sun,
  Moon,
  Zap,
  Leaf,
  MapPin,
  Timer,
  TrendingUp,
  ChevronDown,
  ChevronUp,
  Send,
  BarChart2,
  CloudRain,
} from "lucide-react";

import * as irrigationService from "../services/irrigationService";

// ─── Dispatch type badge config ──────────────────────────────────────
const DISPATCH_BADGE = {
  morning_schedule: { label: "🌅 Morning",  bg: "bg-amber-500/15",   text: "text-amber-400",   border: "border-amber-400/30"  },
  evening_schedule: { label: "🌇 Evening",  bg: "bg-purple-500/15",  text: "text-purple-400",  border: "border-purple-400/30" },
  manual:           { label: "✋ Manual",   bg: "bg-sky-500/15",     text: "text-sky-400",     border: "border-sky-400/30"    },
  threshold:        { label: "⚡ Threshold",bg: "bg-red-500/15",     text: "text-red-400",     border: "border-red-400/30"    },
};

// ─── Risk colour map ─────────────────────────────────────────────────
const RISK_COLORS = {
  High:   "text-red-400",
  Medium: "text-amber-400",
  Low:    "text-emerald-400",
};

// ─── Helper: format UTC date to local string ─────────────────────────
function fmtDate(iso) {
  if (!iso) return "—";
  const d = new Date(iso);
  return d.toLocaleString("en-IN", {
    day: "2-digit", month: "short", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

// ─── Summary stat card ───────────────────────────────────────────────
function StatCard({ icon: Icon, label, value, color = "text-cyan-400", bg = "bg-cyan-500/10" }) {
  return (
    <div className="card p-4 flex items-center gap-4">
      <div className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${bg}`}>
        <Icon size={20} className={color} />
      </div>
      <div>
        <p className="text-xs font-semibold text-field-900/50 dark:text-mist/50 uppercase tracking-wide">{label}</p>
        <p className="text-xl font-bold text-field-900 dark:text-mist mt-0.5">{value}</p>
      </div>
    </div>
  );
}

// ─── Single history row ───────────────────────────────────────────────
function HistoryRow({ record, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const badge = DISPATCH_BADGE[record.dispatch_type] ?? DISPATCH_BADGE.manual;
  const riskColor = RISK_COLORS[record.risk_level] ?? "text-mist/50";

  return (
    <div className={`card overflow-hidden transition-all duration-300 border ${
      record.irrigation_needed ? "border-amber-400/20" : "border-emerald-400/15"
    }`}>
      {/* Row header */}
      <div
        className="flex items-center gap-3 p-4 cursor-pointer hover:bg-field-900/3 dark:hover:bg-mist/3 transition-colors"
        onClick={() => setExpanded((v) => !v)}
      >
        {/* Status icon */}
        <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-xl ${
          record.irrigation_needed ? "bg-amber-500/15" : "bg-emerald-500/15"
        }`}>
          {record.irrigation_needed
            ? <AlertTriangle size={17} className="text-amber-400" />
            : <CheckCircle2  size={17} className="text-emerald-400" />}
        </div>

        {/* Plant info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-sm text-field-900 dark:text-mist truncate">
              {record.plant_name}
            </span>
            <span className="text-[10px] text-field-900/40 dark:text-mist/40 font-medium">
              {record.crop_type}
            </span>
          </div>
          <div className="flex items-center gap-3 mt-0.5 flex-wrap">
            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full border ${badge.bg} ${badge.text} ${badge.border}`}>
              {badge.label}
            </span>
            {record.field_position && (
              <span className="flex items-center gap-1 text-[10px] text-field-900/40 dark:text-mist/40">
                <MapPin size={9} /> {record.field_position}
              </span>
            )}
            <span className="text-[10px] text-field-900/35 dark:text-mist/35 flex items-center gap-1">
              <Calendar size={9} /> {fmtDate(record.recorded_at)}
            </span>
          </div>
        </div>

        {/* Key metrics */}
        <div className="hidden sm:flex items-center gap-4 shrink-0">
          {record.irrigation_frequency && (
            <div className="text-center">
              <p className="text-[10px] text-field-900/40 dark:text-mist/40 uppercase tracking-wide">Frequency</p>
              <p className="text-xs font-bold text-cyan-400">{record.irrigation_frequency}</p>
            </div>
          )}
          {record.irrigation_hours != null && (
            <div className="text-center">
              <p className="text-[10px] text-field-900/40 dark:text-mist/40 uppercase tracking-wide">Duration</p>
              <p className="text-xs font-bold text-emerald-400">{record.irrigation_hours}h</p>
            </div>
          )}
          {record.risk_level && (
            <div className="text-center">
              <p className="text-[10px] text-field-900/40 dark:text-mist/40 uppercase tracking-wide">Risk</p>
              <p className={`text-xs font-bold ${riskColor}`}>{record.risk_level}</p>
            </div>
          )}
          {record.email_sent && (
            <div className="flex h-7 w-7 items-center justify-center rounded-full bg-green-500/15">
              <Send size={12} className="text-green-400" />
            </div>
          )}
        </div>

        {/* Expand toggle */}
        <div className="shrink-0 ml-2 text-field-900/30 dark:text-mist/30">
          {expanded ? <ChevronUp size={15} /> : <ChevronDown size={15} />}
        </div>
      </div>

      {/* Expanded details */}
      {expanded && (
        <div className="border-t border-field-900/6 dark:border-mist/6 px-4 pb-4 pt-3 animate-in fade-in duration-200">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-3">
            {[
              { label: "Soil Moisture", value: record.soil_moisture != null ? `${record.soil_moisture.toFixed(1)}%` : "—", icon: Droplets,    color: "text-cyan-400"    },
              { label: "Temperature",   value: record.temperature   != null ? `${record.temperature}°C`          : "—", icon: TrendingUp,  color: "text-orange-400"  },
              { label: "Water Amount",  value: record.water_quantity ?? "—",                                             icon: Zap,         color: "text-purple-400"  },
              { label: "Rainfall 24h",  value: record.rainfall      != null ? `${record.rainfall} mm`            : "—", icon: CloudRain,   color: "text-blue-400"    },
            ].map(({ label, value, icon: Icon, color }) => (
              <div key={label} className="rounded-xl bg-field-900/4 dark:bg-mist/4 p-3">
                <div className="flex items-center gap-1.5 mb-1">
                  <Icon size={11} className={color} />
                  <span className="text-[10px] text-field-900/40 dark:text-mist/40 uppercase tracking-wide font-semibold">{label}</span>
                </div>
                <p className="text-sm font-bold text-field-900 dark:text-mist">{value}</p>
              </div>
            ))}
          </div>

          {record.timing_advice && (
            <div className="flex items-start gap-2 rounded-xl bg-amber-500/8 border border-amber-400/15 p-3 mb-3">
              <Clock size={13} className="text-amber-400 mt-0.5 shrink-0" />
              <p className="text-xs text-field-900/75 dark:text-mist/75">{record.timing_advice}</p>
            </div>
          )}

          {record.advisory_notes?.length > 0 && (
            <div className="rounded-xl bg-field-900/3 dark:bg-mist/3 p-3 mb-3">
              <p className="text-[10px] font-bold text-field-900/40 dark:text-mist/40 uppercase tracking-wide mb-2">Field Advisory</p>
              <ul className="space-y-1">
                {record.advisory_notes.map((note, i) => (
                  <li key={i} className="flex items-start gap-2 text-xs text-field-900/65 dark:text-mist/65">
                    <span className="text-canopy mt-0.5">•</span>
                    {note}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 text-[10px] text-field-900/35 dark:text-mist/35">
              {record.email_sent && (
                <span className="flex items-center gap-1 text-green-400">
                  <Send size={10} /> Email alert sent to {record.email_recipient || "farmer"}
                </span>
              )}
            </div>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(record.id); }}
              className="flex items-center gap-1.5 rounded-lg px-2.5 py-1.5 text-xs font-semibold text-red-400 hover:bg-red-500/10 transition-colors"
            >
              <Trash2 size={12} /> Delete
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────
export default function IrrigationHistory() {
  const [records,   setRecords]   = useState([]);
  const [total,     setTotal]     = useState(0);
  const [loading,   setLoading]   = useState(false);
  const [dispatching, setDispatching] = useState(null); // "morning" | "evening" | null

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    try {
      const res = await irrigationService.getIrrigationHistory(100, 0);
      setRecords(res.data || []);
      setTotal(res.total || 0);
    } catch {
      toast.error("Failed to load irrigation history.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  async function handleDelete(id) {
    try {
      await irrigationService.deleteHistoryRecord(id);
      toast.success("Record deleted.");
      setRecords((prev) => prev.filter((r) => r.id !== id));
      setTotal((t) => t - 1);
    } catch {
      toast.error("Failed to delete record.");
    }
  }

  async function handleDispatch(type) {
    setDispatching(type);
    try {
      const fn = type === "morning"
        ? irrigationService.triggerMorningDispatch
        : irrigationService.triggerEveningDispatch;
      const res = await fn(false);
      const d = res.data;
      toast.success(
        `${type === "morning" ? "🌅 Morning" : "🌇 Evening"} dispatch complete — ${d.total_alerts} alert(s) sent to ${d.total_plants} plant(s).`,
        { duration: 5000 }
      );
      await fetchHistory();
    } catch {
      toast.error(`${type} dispatch failed. Check backend.`);
    } finally {
      setDispatching(null);
    }
  }

  // Derived stats
  const totalIrrigated   = records.filter((r) => r.irrigation_needed).length;
  const totalEmailsSent  = records.filter((r) => r.email_sent).length;
  const morningCount     = records.filter((r) => r.dispatch_type === "morning_schedule").length;
  const eveningCount     = records.filter((r) => r.dispatch_type === "evening_schedule").length;

  return (
    <div className="min-h-screen bg-mist dark:bg-field-900 p-4 md:p-6 lg:p-8">
      {/* ── Header ── */}
      <div className="mb-6 flex flex-col gap-1">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div className="flex items-center gap-2.5">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-cyan-500/15 text-cyan-400">
              <Droplets size={20} />
            </div>
            <div>
              <h1 className="font-display text-xl font-bold text-field-900 dark:text-mist">
                Irrigation History
              </h1>
              <p className="text-xs text-field-900/50 dark:text-mist/50">
                Automated morning & evening dispatch logs · AI-based irrigation timeline
              </p>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex items-center gap-2 flex-wrap">
            <button
              onClick={() => handleDispatch("morning")}
              disabled={!!dispatching}
              className="flex items-center gap-2 rounded-xl bg-amber-500/12 border border-amber-400/25 px-3.5 py-2 text-xs font-semibold text-amber-400 hover:bg-amber-500/20 transition-colors disabled:opacity-50"
            >
              {dispatching === "morning"
                ? <Loader2 size={13} className="animate-spin" />
                : <Sun size={13} />}
              Morning Dispatch
            </button>
            <button
              onClick={() => handleDispatch("evening")}
              disabled={!!dispatching}
              className="flex items-center gap-2 rounded-xl bg-purple-500/12 border border-purple-400/25 px-3.5 py-2 text-xs font-semibold text-purple-400 hover:bg-purple-500/20 transition-colors disabled:opacity-50"
            >
              {dispatching === "evening"
                ? <Loader2 size={13} className="animate-spin" />
                : <Moon size={13} />}
              Evening Dispatch
            </button>
            <button
              onClick={fetchHistory}
              disabled={loading}
              className="flex items-center gap-2 rounded-xl bg-field-900/6 dark:bg-mist/6 border border-field-900/10 dark:border-mist/10 px-3.5 py-2 text-xs font-semibold text-field-900/70 dark:text-mist/70 hover:bg-field-900/10 dark:hover:bg-mist/10 transition-colors disabled:opacity-50"
            >
              <RefreshCw size={13} className={loading ? "animate-spin" : ""} />
              Refresh
            </button>
          </div>
        </div>
      </div>

      {/* ── Schedule Info Banner ── */}
      <div className="mb-6 rounded-2xl bg-gradient-to-r from-cyan-500/8 via-emerald-500/6 to-purple-500/8 border border-cyan-400/15 p-4">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-canopy/15">
            <Clock size={18} className="text-canopy" />
          </div>
          <div className="flex-1">
            <p className="text-sm font-bold text-field-900 dark:text-mist">Automatic Schedule Active</p>
            <p className="text-xs text-field-900/50 dark:text-mist/50 mt-0.5">
              AgriShield automatically checks all registered plants and sends irrigation alerts twice daily —
              <span className="text-amber-400 font-semibold"> 🌅 6:00 AM (Morning)</span> &
              <span className="text-purple-400 font-semibold"> 🌇 6:00 PM (Evening)</span>.
              Alerts are only sent when water is needed.
            </p>
          </div>
          <div className="flex items-center gap-1.5 rounded-full bg-emerald-500/15 border border-emerald-400/25 px-3 py-1.5">
            <div className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[11px] font-bold text-emerald-400">Scheduler Running</span>
          </div>
        </div>
      </div>

      {/* ── Summary Stats ── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
        <StatCard icon={BarChart2}  label="Total Records"    value={total}           color="text-cyan-400"    bg="bg-cyan-500/10"    />
        <StatCard icon={AlertTriangle} label="Irrigation Needed" value={totalIrrigated}  color="text-amber-400"   bg="bg-amber-500/10"  />
        <StatCard icon={Send}       label="Emails Sent"      value={totalEmailsSent} color="text-green-400"   bg="bg-green-500/10"  />
        <StatCard icon={Timer}      label="Morning / Evening" value={`${morningCount} / ${eveningCount}`} color="text-purple-400" bg="bg-purple-500/10" />
      </div>

      {/* ── History List ── */}
      {loading && records.length === 0 && (
        <div className="card flex flex-col items-center justify-center gap-4 py-16">
          <div className="relative">
            <div className="h-12 w-12 rounded-full border-4 border-cyan-500/20 border-t-cyan-400 animate-spin" />
            <Droplets size={16} className="absolute inset-0 m-auto text-cyan-400" />
          </div>
          <p className="text-sm text-field-900/50 dark:text-mist/50">Loading irrigation history…</p>
        </div>
      )}

      {!loading && records.length === 0 && (
        <div className="card flex flex-col items-center justify-center gap-5 py-20 text-center">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-cyan-500/10">
            <Droplets size={32} className="text-cyan-400" />
          </div>
          <div>
            <h3 className="font-display text-lg font-semibold text-field-900 dark:text-mist">
              No Irrigation History Yet
            </h3>
            <p className="mt-1.5 text-sm text-field-900/45 dark:text-mist/45 max-w-sm mx-auto">
              History will be automatically recorded when the morning or evening dispatch runs,
              or when you manually trigger an irrigation prediction.
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => handleDispatch("morning")}
              disabled={!!dispatching}
              className="flex items-center gap-2 btn-primary px-4 py-2 text-sm"
            >
              <Sun size={14} /> Run Morning Dispatch
            </button>
          </div>
        </div>
      )}

      {records.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between mb-1">
            <p className="text-xs text-field-900/40 dark:text-mist/40 font-medium">
              Showing {records.length} of {total} records · sorted by newest first
            </p>
          </div>
          {records.map((record) => (
            <HistoryRow key={record.id} record={record} onDelete={handleDelete} />
          ))}
        </div>
      )}

      {/* Footer note */}
      <div className="mt-8 flex items-center justify-center gap-1.5 text-[11px] text-field-900/30 dark:text-mist/30">
        <CheckCircle2 size={11} className="text-canopy" />
        AgriShield Irrigation Intelligence · Automated Precision Scheduling
      </div>
    </div>
  );
}
