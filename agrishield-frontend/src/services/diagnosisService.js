import api from "./api";

export const diagnosePlantImage = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api
    .post("/api/plant-diagnosis", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    })
    .then((r) => r.data);
};

export const getDiagnosisHistory = (limit = 20) =>
  api.get(`/api/plant-diagnosis/history?limit=${limit}`).then((r) => r.data);

export const getSupportedClasses = () =>
  api.get("/api/plant-diagnosis/classes").then((r) => r.data);
