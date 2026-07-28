import { createContext, useContext, useEffect, useState } from "react";
import { setAuthToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const stored = window.localStorage.getItem("agrishield-user");
    const token = window.localStorage.getItem("agrishield-token");
    if (stored && token) {
      setUser(JSON.parse(stored));
      setAuthToken(token);
    }
    setLoading(false);
  }, []);

  const login = ({ user: userData, token }) => {
    window.localStorage.setItem("agrishield-user", JSON.stringify(userData));
    window.localStorage.setItem("agrishield-token", token);
    setAuthToken(token);
    setUser(userData);
  };

  const logout = () => {
    window.localStorage.removeItem("agrishield-user");
    window.localStorage.removeItem("agrishield-token");
    setAuthToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
