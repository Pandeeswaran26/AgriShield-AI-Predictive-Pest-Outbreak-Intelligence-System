import api from "./api";

export const predictPest = (payload) => api.post("/predict", payload).then((r) => r.data);

export const predictPestAuto = (cropOrPayload, latitude, longitude) => {
  const payload =
    typeof cropOrPayload === "object" && cropOrPayload !== null
      ? cropOrPayload
      : {
          Crop: cropOrPayload,
          Latitude: latitude,
          Longitude: longitude,
        };
  return api.post("/predict/auto", payload).then((r) => r.data);
};

export const runCropAssessment = (payload) => api.post("/api/assessment/run", payload).then((r) => r.data);

export const explainPrediction = (id) =>
  api.get(`/predict/${id}/explain`).then((r) => r.data);

export const downloadReport = (id) =>
  api.get(`/predict/${id}/report`, { responseType: "blob" }).then((r) => r.data);

