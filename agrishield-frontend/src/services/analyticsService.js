import api from "./api";

export const getPredictionTrends = () =>
  api.get("/analytics/prediction-trends").then((r) => r.data);

export const getCropAnalysis = () => api.get("/analytics/crop-analysis").then((r) => r.data);

export const getWeatherImpact = () => api.get("/analytics/weather-impact").then((r) => r.data);

export const getLocationAnalysis = () =>
  api.get("/analytics/location-analysis").then((r) => r.data);

export const getRiskDistribution = () =>
  api.get("/analytics/risk-distribution").then((r) => r.data);
