import { useEffect, useState } from "react";
import {
  ScanLine,
  AlertTriangle,
  AlertCircle,
  ShieldCheck,
  CalendarClock,
} from "lucide-react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import toast from "react-hot-toast";
import StatCard from "../components/dashboard/StatCard";
import dashboardService from "../services/dashboardService";

const COLORS = ["#22C55E", "#2563EB", "#F59E0B", "#EF4444", "#16A34A"];

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [pestTrend, setPestTrend] = useState([]);
  const [weatherTrend, setWeatherTrend] = useState([]);
  const [monthly, setMonthly] = useState([]);
  const [cropAnalysis, setCropAnalysis] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [s, pt, wt, mp, ca] = await Promise.all([
          dashboardService.getSummary(),
          dashboardService.getPestTrend(),
          dashboardService.getWeatherTrend(),
          dashboardService.getMonthlyPredictions(),
          dashboardService.getCropAnalysis(),
        ]);
        if (!mounted) return;
        setSummary(s);
        setPestTrend(pt || []);
        setWeatherTrend(wt || []);
        setMonthly(mp || []);
        setCropAnalysis(ca || []);
      } catch (err) {
        toast.error(err.message || "Couldn't load dashboard data.");
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const cards = [
    { icon: ScanLine, label: "Total predictions", value: summary?.totalPredictions, tone: "accent" },
    { icon: AlertTriangle, label: "High risk fields", value: summary?.highRisk, tone: "high" },
    { icon: AlertCircle, label: "Medium risk", value: summary?.mediumRisk, tone: "medium" },
    { icon: ShieldCheck, label: "Low risk", value: summary?.lowRisk, tone: "primary" },
    { icon: CalendarClock, label: "Today's predictions", value: summary?.todayPredictions, tone: "accent" },
  ];

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
        {cards.map((c) => (
          <StatCard key={c.label} {...c} value={c.value ?? "—"} loading={loading} />
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="glass-card p-6">
          <h3 className="font-display font-semibold">Pest trend</h3>
          <p className="text-xs text-slate-400">Predicted pest value over recent weeks</p>
          <div className="mt-4 h-64">
            {loading ? (
              <div className="skeleton h-full w-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={pestTrend}>
                  <defs>
                    <linearGradient id="pestFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#22C55E" stopOpacity={0.35} />
                      <stop offset="100%" stopColor="#22C55E" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                  <XAxis dataKey="week" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Area type="monotone" dataKey="value" stroke="#16A34A" fill="url(#pestFill)" />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="font-display font-semibold">Weather trend</h3>
          <p className="text-xs text-slate-400">Temperature &amp; rainfall over time</p>
          <div className="mt-4 h-64">
            {loading ? (
              <div className="skeleton h-full w-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={weatherTrend}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                  <XAxis dataKey="week" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="maxTemp" stroke="#2563EB" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="rainfall" stroke="#22C55E" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="font-display font-semibold">Monthly predictions</h3>
          <p className="text-xs text-slate-400">Volume of predictions run per month</p>
          <div className="mt-4 h-64">
            {loading ? (
              <div className="skeleton h-full w-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={monthly}>
                  <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
                  <XAxis dataKey="month" fontSize={12} />
                  <YAxis fontSize={12} />
                  <Tooltip />
                  <Bar dataKey="count" fill="#22C55E" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="font-display font-semibold">Crop analysis</h3>
          <p className="text-xs text-slate-400">Share of predictions by crop</p>
          <div className="mt-4 h-64">
            {loading ? (
              <div className="skeleton h-full w-full" />
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={cropAnalysis}
                    dataKey="value"
                    nameKey="crop"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={3}
                  >
                    {cropAnalysis.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
