import api from "./api";

export const recommendationService = {
  getRecommendation: (predictionId) =>
    api.get(`/recommendations/${predictionId}`).then((res) => res.data),
};

export default recommendationService;
