import api from "./api";

const weatherService = {
  getCurrentWeather: (lat, lon) =>
    api.get(`/weather/current?lat=${lat}&lon=${lon}`)
      .then((res) => res.data),
};

export default weatherService;