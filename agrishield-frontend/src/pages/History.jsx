import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";
import { Trash2, Download, ClipboardList, History as HistoryIcon } from "lucide-react";
import RiskBadge from "../components/RiskBadge";
import LoadingSpinner from "../components/LoadingSpinner";
import * as historyService from "../services/historyService";

export default function History() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);

  const load = () => {
    setLoading(true);
    historyService
      .getHistory()
      .then((res) => setItems(res.items || []))
      .finally(() => setLoading(false));
  };

  useEffect(load, []);

  const handleDelete = async (id) => {
    setDeletingId(id);
    try {
      await historyService.deletePrediction(id);
      setItems((prev) => prev.filter((i) => i.id !== id));
      toast.success("Prediction deleted");
    } catch {
      toast.error("Could not delete prediction");
    } finally {
      setDeletingId(null);
    }
  };

  const handleExport = async () => {
    try {
      const blob = await historyService.exportHistoryCsv();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "prediction_history.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      toast.error("Could not export history");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h1 className="font-display text-2xl font-semibold">Prediction history</h1>
          <p className="mt-1 text-sm text-field-900/55 dark:text-mist/55">
            Every pest-risk prediction you've run, most recent first.
          </p>
        </div>
        <button onClick={handleExport} className="btn-ghost" disabled={!items.length}>
          <Download size={15} /> Export CSV
        </button>
      </div>

      {loading ? (
        <LoadingSpinner label="Loading history" />
      ) : items.length === 0 ? (
        <div className="card flex flex-col items-center justify-center gap-2 p-14 text-center text-sm text-field-900/45 dark:text-mist/45">
          <HistoryIcon size={22} className="opacity-40" />
          No predictions yet.
          <Link to="/app/predict" className="text-canopy hover:underline">Run your first prediction</Link>
        </div>
      ) : (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-field-900/10 text-xs uppercase tracking-wide text-field-900/50 dark:border-mist/10 dark:text-mist/50">
                <tr>
                  <th className="px-5 py-3">Crop</th>
                  <th className="px-5 py-3">Pest</th>
                  <th className="px-5 py-3">Location</th>
                  <th className="px-5 py-3">Pest value</th>
                  <th className="px-5 py-3">Risk</th>
                  <th className="px-5 py-3">Date</th>
                  <th className="px-5 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-field-900/5 dark:divide-mist/5">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-field-900/[0.02] dark:hover:bg-mist/[0.02]">
                    <td className="px-5 py-3 font-medium">{item.crop}</td>
                    <td className="px-5 py-3">{item.pest_name}</td>
                    <td className="px-5 py-3 text-field-900/70 dark:text-mist/70">{item.location}</td>
                    <td className="px-5 py-3 font-mono">{item.pest_value}</td>
                    <td className="px-5 py-3"><RiskBadge level={item.risk_level} size="sm" /></td>
                    <td className="px-5 py-3 text-xs text-field-900/50 dark:text-mist/50">
                      {new Date(item.prediction_date).toLocaleDateString()}
                    </td>
                    <td className="px-5 py-3">
                      <div className="flex justify-end gap-2">
                        <Link
                          to={`/app/recommendation?id=${item.id}`}
                          className="rounded-lg p-1.5 text-field-900/50 hover:bg-canopy/10 hover:text-canopy dark:text-mist/50"
                          title="View recommendation"
                        >
                          <ClipboardList size={16} />
                        </Link>
                        <button
                          onClick={() => handleDelete(item.id)}
                          disabled={deletingId === item.id}
                          className="rounded-lg p-1.5 text-field-900/50 hover:bg-alert/10 hover:text-alert dark:text-mist/50"
                          title="Delete"
                        >
                          <Trash2 size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}
