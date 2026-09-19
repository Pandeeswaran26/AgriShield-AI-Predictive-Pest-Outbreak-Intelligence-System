import api from "./api";

export const getSummary = () => api.get("/dashboard/summary").then((r) => r.data);

export const getLatestPrediction = () => api.get("/dashboard/latest").then((r) => r.data);

export const getPestTrend = () => api.get("/dashboard/pest-trend").then((r) => r.data);

export const getWeatherTrend = () => api.get("/dashboard/weather-trend").then((r) => r.data);

export const getMonthlyPredictions = () =>
  api.get("/dashboard/monthly-predictions").then((r) => r.data);

export const getCropAnalysis = () => api.get("/dashboard/crop-analysis").then((r) => r.data);

export const getFieldsOverview = () => api.get("/dashboard/fields").then((r) => r.data);

