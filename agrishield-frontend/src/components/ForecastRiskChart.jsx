import React from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import { Calendar, CloudRain, Thermometer, Wind } from "lucide-react";

export default function ForecastRiskChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 text-sm bg-slate-900/40 rounded-xl border border-slate-800">
        No 7-day forecast data available.
      </div>
    );
  }

  const chartData = data.map((d) => ({
    date: d.date ? d.date.slice(5) : d.day_name,
    dayName: d.day_name,
    pestValue: d.pest_value || 0,
    maxT: d.max_t,
    minT: d.min_t,
    rain: d.rf,
    wind: d.ws,
    topPest: d.top_pest_display || d.top_pest,
    riskLevel: d.risk_level,
  }));

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload.length) {
      const item = payload[0].payload;
      return (
        <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs space-y-1 z-50">
          <p className="font-bold text-slate-200 border-b border-slate-800 pb-1 flex items-center gap-1.5">
            <Calendar className="w-3.5 h-3.5 text-emerald-400" />
            {item.dayName} ({item.date})
          </p>
          <div className="pt-1 space-y-1">
            <p className="text-slate-300 font-medium">
              Top Risk: <span className="text-emerald-400">{item.topPest}</span>
            </p>
            <p className="text-slate-400">
              Risk Level:{" "}
              <span
                className={`font-semibold ${
                  item.riskLevel === "High"
                    ? "text-rose-400"
                    : item.riskLevel === "Medium"
                    ? "text-amber-400"
                    : "text-teal-400"
                }`}
              >
                {item.riskLevel} ({item.pestValue.toFixed(2)})
              </span>
            </p>
            <div className="flex items-center gap-3 text-slate-400 pt-1 border-t border-slate-800/80 text-[11px]">
              <span className="flex items-center gap-1">
                <Thermometer className="w-3 h-3 text-amber-400" />
                {item.maxT}°C
              </span>
              <span className="flex items-center gap-1">
                <CloudRain className="w-3 h-3 text-sky-400" />
                {item.rain}mm
              </span>
              <span className="flex items-center gap-1">
                <Wind className="w-3 h-3 text-slate-400" />
                {item.wind}km/h
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="w-full bg-slate-900/60 p-4 rounded-xl border border-slate-800">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
        <div>
          <h4 className="font-semibold text-slate-200 text-sm flex items-center gap-2">
            <Calendar className="w-4 h-4 text-emerald-400" />
            7-Day Pest Outbreak Risk Timeline
          </h4>
          <p className="text-xs text-slate-400">
            Projected risk trend driven by daily Open-Meteo weather parameters
          </p>
        </div>
        <div className="flex items-center gap-2 text-[11px] text-slate-400">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-500 inline-block" /> High
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" /> Medium
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" /> Low
          </span>
        </div>
      </div>

      <div className="h-56 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <YAxis stroke="#64748b" tick={{ fill: "#94a3b8", fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Area
              type="monotone"
              dataKey="pestValue"
              stroke="#10b981"
              strokeWidth={2.5}
              fillOpacity={1}
              fill="url(#riskGrad)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
