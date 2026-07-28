import api from "./api";

export const authService = {
  loginFarmer: (credentials) =>
    api.post("/auth/farmer/login", credentials).then((res) => res.data),

  loginAdmin: (credentials) =>
    api.post("/auth/admin/login", credentials).then((res) => res.data),

  register: (payload) =>
    api.post("/auth/register", payload).then((res) => res.data),

  logout: () => api.post("/auth/logout").then((res) => res.data),
};

export default authService;
