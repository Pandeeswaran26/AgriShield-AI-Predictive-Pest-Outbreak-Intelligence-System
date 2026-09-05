import api from "./api";

export const getRecommendation = (predictionId) =>
  api.get(`/recommendations/${predictionId}`).then((r) => r.data);
