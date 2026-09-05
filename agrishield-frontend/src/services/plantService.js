import api from "./api";

export const getPlants = () => api.get("/plants").then((r) => r.data);

export const getPlant = (id) => api.get(`/plants/${id}`).then((r) => r.data);

export const createPlant = (data) => api.post("/plants", data).then((r) => r.data);

export const updatePlant = (id, data) => api.put(`/plants/${id}`, data).then((r) => r.data);

export const deletePlant = (id) => api.delete(`/plants/${id}`).then((r) => r.data);
