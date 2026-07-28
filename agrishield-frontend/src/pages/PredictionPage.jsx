import { useState } from "react";
import { useForm } from "react-hook-form";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, ScanLine, Download, RefreshCcw } from "lucide-react";
import toast from "react-hot-toast";
import predictService from "../services/predictService";
import RiskMeter from "../components/prediction/RiskMeter";
import RiskBadge from "../components/common/RiskBadge";
import { formatPercent } from "../utils/risk";
import weatherService from "../services/weatherService";  

const CROPS = ["Cotton", "Rice", "Wheat", "Sugarcane", "Maize"];

const FIELDS = [
  { name: "crop", label: "Crop", type: "select", options: CROPS },
  { name: "pestName", label: "Pest name", type: "text", placeholder: "e.g. Aphid" },
  { name: "location", label: "Location", type: "text", placeholder: "e.g. Coimbatore" },
  { name: "observationYear", label: "Observation year", type: "number", placeholder: "2026" },
  { name: "standardWeek", label: "Standard week", type: "number", placeholder: "1-52" },
  { name: "maxTemperature", label: "Maximum temperature (°C)", type: "number", step: "0.1" },
  { name: "minTemperature", label: "Minimum temperature (°C)", type: "number", step: "0.1" },
  { name: "humidity1", label: "Humidity 1 (%)", type: "number", step: "0.1" },
  { name: "humidity2", label: "Humidity 2 (%)", type: "number", step: "0.1" },
  { name: "rainfall", label: "Rainfall (mm)", type: "number", step: "0.1" },
  { name: "windSpeed", label: "Wind speed (km/h)", type: "number", step: "0.1" },
  { name: "sunshineHours", label: "Sunshine hours", type: "number", step: "0.1" },
  { name: "evaporation", label: "Evaporation (mm)", type: "number", step: "0.1" },
];

export default function PredictionPage() {
  const [result, setResult] = useState(null);
  const [downloading, setDownloading] = useState(false);

   const handleGetWeather = async () => {
  if (!navigator.geolocation) {
    alert("Geolocation is not supported by your browser.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (position) => {
      const latitude = position.coords.latitude;
      const longitude = position.coords.longitude;

      try {
        const weather = await weatherService.getCurrentWeather(
          latitude,
          longitude
);

console.log(weather);
setValue("maxTemperature", weather.temperature);
setValue("minTemperature", weather.temperature - 4);
setValue("humidity1", weather.humidity);
setValue("humidity2", weather.humidity);
setValue("rainfall", weather.rainfall);
setValue("windSpeed", weather.wind_speed);

        alert("Weather fetched successfully!");
      } catch (error) {
        console.error(error);
        alert("Failed to fetch weather.");
      }
    },
    (error) => {
      alert("Unable to get your location.");
      console.error(error);
    }
  );
};

const {
  register,
  handleSubmit,
  reset,
  setValue,
  formState: { errors, isSubmitting },
} = useForm();

 const onSubmit = async (values) => {
  console.log(values);

  try {
    const data = await predictService.predict(values);
    setResult(data);
    toast.success("Prediction complete");
  } catch (err) {
    toast.error(err.message || "Prediction failed. Please try again.");
  }
};

  const handleDownload = async () => {
    if (!result?.predictionId) return;
    setDownloading(true);
    try {
      const blob = await predictService.downloadReport(result.predictionId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `agrishield-prediction-${result.predictionId}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      toast.error(err.message || "Couldn't download the report.");
    } finally {
      setDownloading(false);
    }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <form onSubmit={handleSubmit(onSubmit)} className="glass-card space-y-5 p-6 lg:col-span-3">
        <div>
          <h2 className="font-display text-lg font-semibold">Run a prediction</h2>
          <p className="text-sm text-slate-400">
            Enter field and weather readings for the standard week you want to assess.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          {FIELDS.map((f) => (
            <div key={f.name} className={f.type === "select" ? "sm:col-span-2" : ""}>
              <label className="mb-1.5 block text-sm font-medium">{f.label}</label>
              {f.type === "select" ? (
                <select
                  className="input-field"
                  {...register(f.name, { required: `${f.label} is required` })}
                >
                  <option value="">Select {f.label.toLowerCase()}</option>
                  {f.options.map((opt) => (
                    <option key={opt} value={opt}>
                      {opt}
                    </option>
                  ))}
                </select>
              ) : (
                <input
                  type={f.type}
                  step={f.step}
                  placeholder={f.placeholder}
                  className="input-field"
                  {...register(f.name, { required: `${f.label} is required` })}
                />
              )}
              {errors[f.name] && (
                <p className="mt-1 text-xs text-red-500">{errors[f.name].message}</p>
              )}
            </div>
          ))}
        </div>

<div className="flex gap-3 pt-2">

  <button
    type="button"
    onClick={handleGetWeather}
    className="btn-secondary"
  >
    📍 Get Weather
  </button>

  <button
    type="submit"
    disabled={isSubmitting}
    className="btn-primary flex-1 py-2.5"
  >
    {isSubmitting ? (
      <Loader2 size={18} className="animate-spin" />
    ) : (
      <>
        <ScanLine size={18} />
        <span className="ml-2">Predict</span>
      </>
    )}
  </button>

  <button
    type="button"
    onClick={() => {
      reset();
      setResult(null);
    }}
    className="btn-secondary px-4"
  >
    <RefreshCcw size={16} />
  </button>

</div>
      </form>

      <div className="lg:col-span-2">
        <AnimatePresence mode="wait">
          {result ? (
            <motion.div
              key="result"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="glass-card flex flex-col items-center p-6 text-center"
            >
              <RiskMeter score={result.riskScore} level={result.riskLevel} />

              <div className="mt-4">
                <RiskBadge level={result.riskLevel} />
              </div>

              <div className="mt-6 grid w-full grid-cols-2 gap-3 text-left">
                <div className="rounded-xl bg-slate-50 p-3 dark:bg-white/5">
                  <p className="text-xs text-slate-400">Confidence</p>
                  <p className="font-mono text-lg font-semibold">
                    {formatPercent(result.confidence)}
                  </p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3 dark:bg-white/5">
                  <p className="text-xs text-slate-400">Predicted pest value</p>
                  <p className="font-mono text-lg font-semibold">{result.pestValue ?? "—"}</p>
                </div>
              </div>

              <div className="mt-4 w-full rounded-xl bg-slate-50 p-4 text-left dark:bg-white/5">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Recommendation
                </p>
                <p className="mt-1 text-sm text-slate-600 dark:text-slate-300">
                  {result.recommendation ||
                    "Monitor the field closely and re-check after the next rainfall event."}
                </p>
              </div>

              <button
                onClick={handleDownload}
                disabled={downloading}
                className="btn-secondary mt-6 w-full py-2.5"
              >
                {downloading ? (
                  <Loader2 size={16} className="animate-spin" />
                ) : (
                  <>
                    <Download size={16} /> Download report
                  </>
                )}
              </button>
            </motion.div>
          ) : (
            <motion.div
              key="empty"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="glass-card flex h-full min-h-[24rem] flex-col items-center justify-center p-6 text-center text-slate-400"
            >
              <ScanLine size={32} className="mb-3 text-slate-300 dark:text-slate-600" />
              <p className="text-sm">
                Fill in the field readings and run a prediction to see the risk meter here.
              </p>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
