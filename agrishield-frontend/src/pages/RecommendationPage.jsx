import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { ShieldCheck, Sprout, FlaskConical, Leaf as LeafIcon, TrendingDown } from "lucide-react";
import toast from "react-hot-toast";
import recommendationService from "../services/recommendationService";

const SECTIONS = [
  { key: "suggestedActions", title: "Suggested actions", icon: ShieldCheck },
  { key: "prevention", title: "Prevention", icon: Sprout },
  { key: "recommendedPesticides", title: "Recommended pesticides", icon: FlaskConical },
  { key: "organicAlternatives", title: "Organic alternatives", icon: LeafIcon },
];

export default function RecommendationPage() {
  const [searchParams] = useSearchParams();
  const predictionId = searchParams.get("predictionId");
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(Boolean(predictionId));

  useEffect(() => {
    if (!predictionId) return;
    (async () => {
      try {
        const res = await recommendationService.getRecommendation(predictionId);
        setData(res);
      } catch (err) {
        toast.error(err.message || "Couldn't load recommendation.");
      } finally {
        setLoading(false);
      }
    })();
  }, [predictionId]);

  if (!predictionId) {
    return (
      <div className="glass-card flex min-h-[24rem] flex-col items-center justify-center p-8 text-center text-slate-400">
        <Sprout size={32} className="mb-3 text-slate-300 dark:text-slate-600" />
        <p className="text-sm">
          Run a prediction first, then open its recommendation from the prediction result or
          history table.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="glass-card p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="font-display text-lg font-semibold">Recommendation</h2>
            <p className="text-sm text-slate-400">For prediction #{predictionId}</p>
          </div>
          {data?.expectedYieldImpact !== undefined && (
            <div className="flex items-center gap-2 rounded-xl bg-red-50 px-4 py-2 text-red-600 dark:bg-red-500/10 dark:text-red-400">
              <TrendingDown size={16} />
              <div>
                <p className="text-xs">Expected yield impact</p>
                <p className="font-mono font-semibold">{data.expectedYieldImpact}%</p>
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-6 sm:grid-cols-2">
        {SECTIONS.map(({ key, title, icon: Icon }) => (
          <div key={key} className="glass-card p-6">
            <div className="flex items-center gap-2">
              <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary-50 text-primary-600 dark:bg-primary-500/10 dark:text-primary-400">
                <Icon size={16} />
              </span>
              <h3 className="font-display font-semibold">{title}</h3>
            </div>

            <div className="mt-4 space-y-2">
              {loading ? (
                [...Array(3)].map((_, i) => <div key={i} className="skeleton h-4 w-full" />)
              ) : data?.[key]?.length ? (
                <ul className="space-y-2">
                  {data[key].map((item, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-slate-600 dark:text-slate-300">
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-primary-500" />
                      {item}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-sm text-slate-400">No data available for this section yet.</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
