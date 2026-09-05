import { createContext, useContext, useEffect, useState } from "react";
import * as authService from "../services/authService";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const raw = localStorage.getItem("agrishield_user");
    return raw ? JSON.parse(raw) : null;
  });
  const [token, setToken] = useState(() => localStorage.getItem("agrishield_token"));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Confirm the stored token is still valid on load.
    if (!token) {
      setLoading(false);
      return;
    }
    authService
      .getMe()
      .then((data) => {
        const nextUser = {
          user_id: data.user_id,
          name: data.name,
          email: data.email,
          phone: data.phone,
          location: data.location,
        };
        setUser(nextUser);
        localStorage.setItem("agrishield_user", JSON.stringify(nextUser));
      })
      .catch(() => {
        setUser(null);
        setToken(null);
        localStorage.removeItem("agrishield_token");
        localStorage.removeItem("agrishield_user");
      })
      .finally(() => setLoading(false));
  }, [token]);

  const applySession = (data) => {
    const nextUser = {
      user_id: data.user_id,
      name: data.name,
      email: data.email,
      phone: data.phone,
      location: data.location,
    };
    localStorage.setItem("agrishield_token", data.token);
    localStorage.setItem("agrishield_user", JSON.stringify(nextUser));
    setToken(data.token);
    setUser(nextUser);
  };

  const login = async (email, password) => {
    const data = await authService.login({ email, password });
    applySession(data);
    return data;
  };

  const verifyOtp = async (email, otp) => {
    const data = await authService.verifyOtp({ email, otp });
    applySession(data);
    return data;
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch {
      // Token may already be invalid — clear local session regardless.
    }
    localStorage.removeItem("agrishield_token");
    localStorage.removeItem("agrishield_user");
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, token, loading, login, verifyOtp, logout, isAuthenticated: !!token }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
