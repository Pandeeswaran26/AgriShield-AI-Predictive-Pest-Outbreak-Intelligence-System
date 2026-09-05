import api from "./api";

export const getHistory = () => api.get("/history").then((r) => r.data);

export const deletePrediction = (id) => api.delete(`/history/${id}`).then((r) => r.data);

export const exportHistoryCsv = () =>
  api.get("/history/export", { responseType: "blob" }).then((r) => r.data);
