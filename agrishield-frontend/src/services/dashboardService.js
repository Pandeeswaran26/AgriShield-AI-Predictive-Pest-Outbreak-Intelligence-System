import api from "./api";

export const dashboardService = {
  getSummary: () => api.get("/dashboard/summary").then((res) => res.data),

  getPestTrend: (range = "30d") =>
    api.get("/dashboard/pest-trend", { params: { range } }).then((res) => res.data),

  getWeatherTrend: (range = "30d") =>
    api.get("/dashboard/weather-trend", { params: { range } }).then((res) => res.data),

  getMonthlyPredictions: () =>
    api.get("/dashboard/monthly-predictions").then((res) => res.data),

  getCropAnalysis: () =>
    api.get("/dashboard/crop-analysis").then((res) => res.data),
};

export default dashboardService;
