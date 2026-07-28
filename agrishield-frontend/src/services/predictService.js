  import api from "./api";

  /**
   * Payload shape expected by the FastAPI /predict endpoint.
   * Field names mirror the columns the ExtraTreesRegressor was trained on
   * (see train_final_model.py / advanced_feature_engineering.py):
   * Crop, Pest_Name, Location, Observation Year, Standard Week,
   * MaxT, MinT, RH1(%), RH2(%), RF(mm), WS(kmph), SSH(hrs), EVP(mm).
   */
  export const predictService = {
    predict: (formValues) => {
      const payload = {
  Crop: formValues.crop,
  Pest_Name: formValues.pestName,
  Location: formValues.location,

  Observation_Year: Number(formValues.observationYear),
  Standard_Week: Number(formValues.standardWeek),

  MaxT: Number(formValues.maxTemperature),
  MinT: Number(formValues.minTemperature),

  RH1: Number(formValues.humidity1),
  RH2: Number(formValues.humidity2),

  RF: Number(formValues.rainfall),
  WS: Number(formValues.windSpeed),

  SSH: Number(formValues.sunshineHours),
  EVP: Number(formValues.evaporation),
};
      console.log(payload);
      return api.post("/predict", payload).then((res) => res.data);
    },

    // SHAP-based explanation for a given prediction id.
    explain: (predictionId) =>
      api.get(`/predict/${predictionId}/explain`).then((res) => res.data),

    downloadReport: (predictionId) =>
      api
        .get(`/predict/${predictionId}/report`, { responseType: "blob" })
        .then((res) => res.data),
  };

  export default predictService;
