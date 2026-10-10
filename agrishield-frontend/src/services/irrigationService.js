import api from "./api";

export const predictIrrigation = (data) =>
  api.post("/irrigation/predict", data).then((r) => r.data);

export const getSupportedCrops = () =>
  api.get("/irrigation/crops").then((r) => r.data);

export const getModelMetadata = () =>
  api.get("/irrigation/metadata").then((r) => r.data);

export const sendIrrigationAlert = (data) =>
  api.post("/irrigation/send-alert", data).then((r) => r.data);

// ─── Irrigation History ───────────────────────────────────────────────
export const getIrrigationHistory = (limit = 50, offset = 0) =>
  api.get(`/irrigation/history?limit=${limit}&offset=${offset}`).then((r) => r.data);

export const logIrrigationEvent = (data) =>
  api.post("/irrigation/history/log", data).then((r) => r.data);

export const getHistoryRecord = (id) =>
  api.get(`/irrigation/history/${id}`).then((r) => r.data);

export const deleteHistoryRecord = (id) =>
  api.delete(`/irrigation/history/${id}`).then((r) => r.data);

export const triggerMorningDispatch = (force = false) =>
  api.post("/irrigation/history/send-morning", { force_send: force }).then((r) => r.data);

export const triggerEveningDispatch = (force = false) =>
  api.post("/irrigation/history/send-evening", { force_send: force }).then((r) => r.data);
