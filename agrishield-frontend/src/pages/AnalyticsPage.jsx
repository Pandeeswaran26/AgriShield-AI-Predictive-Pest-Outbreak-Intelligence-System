import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import toast from "react-hot-toast";
import analyticsService from "../services/analyticsService";

const COLORS = ["#22C55E", "#2563EB", "#F59E0B", "#EF4444", "#16A34A", "#0EA5E9"];

export default function AnalyticsPage() {
  const [trends, setTrends] = useState([]);
  const [cropAnalysis, setCropAnalysis] = useState([]);
  const [weatherImpact, setWeatherImpact] = useState([]);
  const [locationAnalysis, setLocationAnalysis] = useState([]);
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      analyticsService.getPredictionTrends(),
      analyticsService.getCropAnalysis(),
      analyticsService.getWeatherImpact(),
      analyticsService.getLocationAnalysis(),
      analyticsService.getRiskDistribution(),
    ])
      .then(([t, c, w, l, r]) => {
        if (!mounted) return;
        setTrends(t || []);
        setCropAnalysis(c || []);
        setWeatherImpact(w || []);
        setLocationAnalysis(l || []);
        setRiskDistribution(r || []);
      })
      .catch((err) => toast.error(err.message || "Couldn't load analytics."))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, []);

  const Panel = ({ title, subtitle, children }) => (
    <div className="glass-card p-6">
      <h3 className="font-display font-semibold">{title}</h3>
      <p className="text-xs text-slate-400">{subtitle}</p>
      <div className="mt-4 h-72">{loading ? <div className="skeleton h-full w-full" /> : children}</div>
    </div>
  );

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <Panel title="Prediction trends" subtitle="Risk score over the last predictions">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
            <XAxis dataKey="label" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Line type="monotone" dataKey="riskScore" stroke="#22C55E" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </Panel>

      <Panel title="Crop analysis" subtitle="Average risk score by crop">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={cropAnalysis}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
            <XAxis dataKey="crop" fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip />
            <Bar dataKey="avgRisk" fill="#2563EB" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Panel>

      <Panel title="Weather impact" subtitle="Which weather factors correlate with risk">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={weatherImpact}>
            <PolarGrid />
            <PolarAngleAxis dataKey="factor" fontSize={12} />
            <PolarRadiusAxis fontSize={10} />
            <Radar dataKey="impact" stroke="#22C55E" fill="#22C55E" fillOpacity={0.35} />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </Panel>

      <Panel title="Location analysis" subtitle="Prediction volume by location">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={locationAnalysis} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" opacity={0.15} />
            <XAxis type="number" fontSize={12} />
            <YAxis dataKey="location" type="category" width={90} fontSize={12} />
            <Tooltip />
            <Bar dataKey="count" fill="#16A34A" radius={[0, 6, 6, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Panel>

      <Panel title="Risk distribution" subtitle="Share of predictions per risk band">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie data={riskDistribution} dataKey="value" nameKey="level" innerRadius={60} outerRadius={95} paddingAngle={3}>
              {riskDistribution.map((_, i) => (
                <Cell key={i} fill={COLORS[i % COLORS.length]} />
              ))}
            </Pie>
            <Legend />
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </Panel>
    </div>
  );
}
