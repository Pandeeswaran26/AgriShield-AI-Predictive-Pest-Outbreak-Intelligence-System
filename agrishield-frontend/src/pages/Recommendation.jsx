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
} from "lucide-react";
import RiskBadge from "../components/RiskBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import SmartAdvisory from "../components/SmartAdvisory";
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
      .then(setData)
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

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl md:text-3xl font-bold text-slate-100 flex items-center gap-2">
            <ClipboardList className="w-6 h-6 text-emerald-400" />
            Field Treatment & Smart Advisory
          </h1>
          <p className="mt-1 text-sm text-slate-400">
            Segregated Integrated Pest Management (IPM), crop nutrition schedules, and spray timing windows.
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
                a.download = `treatment_plan_${selectedId}.pdf`;
                a.click();
                window.URL.revokeObjectURL(url);
                toast.success("Executive PDF report downloaded");
              } catch {
                toast.error("Download failed");
              }
            }}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-semibold text-slate-200 border border-slate-700 flex items-center gap-2 transition"
          >
            <FileDown className="w-4 h-4" /> Export Report (PDF)
          </button>
        )}
      </div>

      {/* Select Prediction Dropdown */}
      <div className="bg-slate-900/80 p-4 rounded-2xl border border-slate-800 shadow-xl">
        <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
          Select Historical Surveillance Record
        </label>
        <div className="relative">
          <Search
            size={16}
            className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-500"
          />
          <select
            className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-950 border border-slate-800 text-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500/40"
            value={selectedId}
            onChange={(e) => handleSelect(e.target.value)}
          >
            <option value="">Choose a surveillance entry…</option>
            {history.map((h) => (
              <option key={h.id} value={h.id}>
                #{h.id} — {h.crop} · {h.pest_name} · Risk: {h.risk_level} ({h.location_display || h.location})
              </option>
            ))}
          </select>
        </div>
      </div>

      {loading && <LoadingSpinner label="Loading treatment plan" />}

      {!loading && data && (
        <div className="space-y-6 animate-fadeIn">
          {/* Main Structured Smart Advisory Display */}
          <SmartAdvisory advisory={data} />
        </div>
      )}

      {!loading && !data && selectedId === "" && (
        <div className="bg-slate-900/40 p-12 rounded-2xl border border-slate-800 text-center space-y-3">
          <Sprout size={32} className="mx-auto text-slate-600" />
          <p className="text-sm text-slate-400">
            Select an outbreak prediction from the dropdown above to review its full treatment advisory.
          </p>
          <Link
            to="/app/predict"
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-emerald-400 hover:underline"
          >
            Run New Analysis <ArrowRight size={13} />
          </Link>
        </div>
      )}
    </div>
  );
}
