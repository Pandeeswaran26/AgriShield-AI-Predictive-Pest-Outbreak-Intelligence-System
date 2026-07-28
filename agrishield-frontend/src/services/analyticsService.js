import api from "./api";

export const analyticsService = {
  getPredictionTrends: (params = {}) =>
    api.get("/analytics/prediction-trends", { params }).then((res) => res.data),

  getCropAnalysis: (params = {}) =>
    api.get("/analytics/crop-analysis", { params }).then((res) => res.data),

  getWeatherImpact: (params = {}) =>
    api.get("/analytics/weather-impact", { params }).then((res) => res.data),

  getLocationAnalysis: (params = {}) =>
    api.get("/analytics/location-analysis", { params }).then((res) => res.data),

  getRiskDistribution: (params = {}) =>
    api.get("/analytics/risk-distribution", { params }).then((res) => res.data),
};

export default analyticsService;
