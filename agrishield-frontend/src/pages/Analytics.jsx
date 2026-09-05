import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";
import { Link } from "react-router-dom";
import { ArrowRight, BarChart3 } from "lucide-react";
import LoadingSpinner from "../components/LoadingSpinner";
import * as analyticsService from "../services/analyticsService";

const RISK_COLORS = { Low: "#22C55E", Medium: "#D97706", High: "#DC2626" };

export default function Analytics() {
  const [trends, setTrends] = useState([]);
  const [cropAnalysis, setCropAnalysis] = useState([]);
  const [weatherImpact, setWeatherImpact] = useState([]);
  const [locationAnalysis, setLocationAnalysis] = useState([]);
  const [riskDistribution, setRiskDistribution] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      analyticsService.getPredictionTrends(),
      analyticsService.getCropAnalysis(),
      analyticsService.getWeatherImpact(),
      analyticsService.getLocationAnalysis(),
      analyticsService.getRiskDistribution(),
    ])
      .then(([t, c, w, l, r]) => {
        setTrends(t || []);
        setCropAnalysis(c || []);
        setWeatherImpact(w || []);
        setLocationAnalysis(l || []);
        setRiskDistribution(r || []);
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner label="Loading intelligence analytics" />;

  const hasRiskData = riskDistribution.some((r) => r.value > 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold">Pest Outbreak Analytics</h1>
        <p className="mt-1 text-sm text-field-900/55 dark:text-mist/55">
          Real-time aggregations across risk severity, crop vulnerabilities, weather triggers, and geographical zones.
        </p>
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <ChartCard title="Weekly Pest Risk Score Trend" hasData={trends.length > 0}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.08} />
              <XAxis dataKey="label" fontSize={11} tickLine={false} />
              <YAxis fontSize={11} tickLine={false} />
              <Tooltip cursor={{ stroke: "#22C55E", strokeWidth: 1 }} />
              <Line
                type="monotone"
                dataKey="riskScore"
                name="Avg Risk Score"
                stroke="#22C55E"
                strokeWidth={2.5}
                dot={{ r: 4, fill: "#22C55E" }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Risk Level Distribution" hasData={hasRiskData}>
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={riskDistribution}
                dataKey="value"
                nameKey="level"
                innerRadius={55}
                outerRadius={85}
                paddingAngle={4}
              >
                {riskDistribution.map((entry) => (
                  <Cell key={entry.level} fill={RISK_COLORS[entry.level] || "#94A3B8"} />
                ))}
              </Pie>
              <Legend verticalAlign="bottom" height={36} />
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Average Pest Pressure by Crop" hasData={cropAnalysis.length > 0}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={cropAnalysis}>
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.08} />
              <XAxis dataKey="crop" fontSize={11} tickLine={false} />
              <YAxis fontSize={11} tickLine={false} />
              <Tooltip cursor={{ fill: "rgba(37,99,235,0.06)" }} />
              <Bar dataKey="avgRisk" name="Avg Risk Score" fill="#2563EB" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="Weather Trigger Impact on Pest Activity" hasData={weatherImpact.length > 0}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={weatherImpact} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.08} />
              <XAxis type="number" fontSize={11} tickLine={false} domain={[0, 100]} />
              <YAxis dataKey="factor" type="category" fontSize={11} width={130} tickLine={false} />
              <Tooltip cursor={{ fill: "rgba(22,163,74,0.06)" }} />
              <Bar dataKey="impact" name="Impact Index (%)" fill="#16A34A" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Predictions by Geographical Location" tall hasData={locationAnalysis.length > 0}>
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={locationAnalysis}>
            <CartesianGrid strokeDasharray="3 3" stroke="currentColor" opacity={0.08} />
            <XAxis dataKey="location" fontSize={11} tickLine={false} />
            <YAxis fontSize={11} allowDecimals={false} tickLine={false} />
            <Tooltip cursor={{ fill: "rgba(217,119,6,0.06)" }} />
            <Bar dataKey="count" name="Prediction Count" fill="#D97706" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>
    </div>
  );
}

function ChartCard({ title, children, tall, hasData = true }) {
  return (
    <div className="card p-5">
      <h2 className="font-display text-base font-semibold">{title}</h2>
      <div className={tall ? "mt-4 h-72" : "mt-4 h-64"}>
        {hasData ? (
          children
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-sm text-field-900/40 dark:text-mist/40">
            <BarChart3 size={24} className="opacity-30" />
            <p>No historical predictions logged yet.</p>
            <Link to="/app/predict" className="inline-flex items-center gap-1 text-xs text-canopy hover:underline">
              Run a prediction <ArrowRight size={12} />
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
