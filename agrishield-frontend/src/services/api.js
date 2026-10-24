import axios from "axios";

export const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (typeof window !== "undefined") {
    const { hostname } = window.location;
    if (hostname === "localhost" || hostname === "127.0.0.1") {
      return "";
    }
    if (hostname && (!envUrl || envUrl.includes("localhost") || envUrl.includes("127.0.0.1"))) {
      return `http://${hostname}:8000`;
    }
  }
  return envUrl || "";
};

const api = axios.create({
  baseURL: getApiBaseUrl(),
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("agrishield_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const isAuthEndpoint = error.config?.url?.includes("/auth/");
      const isLoginPage =
        typeof window !== "undefined" &&
        (window.location.pathname.startsWith("/login") || window.location.pathname.startsWith("/register"));
      if (!isAuthEndpoint) {
        localStorage.removeItem("agrishield_token");
        localStorage.removeItem("agrishield_user");
        if (!isLoginPage) {
          window.location.href = "/login";
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
