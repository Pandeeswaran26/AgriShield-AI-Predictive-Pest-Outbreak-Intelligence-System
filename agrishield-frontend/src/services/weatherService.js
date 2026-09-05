import api from "./api";

export const getCurrentWeather = (lat, lon) =>
  api.get("/weather/current", { params: { lat, lon } }).then((r) => r.data);

export const getWeatherForLocation = (location) =>
  api.get("/weather/location", { params: { location } }).then((r) => r.data);

export const getWeatherForCoordinates = (lat, lon) =>
  api.get("/weather/coordinates", { params: { lat, lon } }).then((r) => r.data);

export const get7DayForecast = (lat, lon) =>
  api.get("/weather/forecast", { params: { lat, lon } }).then((r) => r.data);

export const searchLocations = (query) =>
  api.get("/weather/search", { params: { query } }).then((r) => r.data);

