import { useEffect } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "react-hot-toast";

import PublicLayout from "./layouts/PublicLayout";
import DashboardLayout from "./layouts/DashboardLayout";
import ProtectedRoute from "./components/ProtectedRoute";

import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Predict from "./pages/Predict";
import Recommendation from "./pages/Recommendation";
import History from "./pages/History";
import Analytics from "./pages/Analytics";
import Assistant from "./pages/Assistant";
import Settings from "./pages/Settings";
import PlantDiagnosis from "./pages/PlantDiagnosis";


export default function App() {
  useEffect(() => {
    const dark = localStorage.getItem("agrishield_theme") !== "light";
    document.documentElement.classList.toggle("dark", dark);
  }, []);

  return (
    <>
      <Toaster
        position="top-right"
        toastOptions={{
          style: { background: "#101D18", color: "#F5F7F5", fontSize: "13px" },
          success: { iconTheme: { primary: "#22C55E", secondary: "#101D18" } },
          error: { iconTheme: { primary: "#DC2626", secondary: "#101D18" } },
        }}
      />
      <Routes>
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Landing />} />
        </Route>

        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/app"
          element={
            <ProtectedRoute>
              <DashboardLayout />
            </ProtectedRoute>
          }
        >
          <Route index element={<Navigate to="dashboard" replace />} />
          <Route path="dashboard" element={<Dashboard />} />
          <Route path="diagnosis" element={<PlantDiagnosis />} />
          <Route path="predict" element={<Predict />} />

          <Route path="recommendation" element={<Recommendation />} />
          <Route path="history" element={<History />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="assistant" element={<Assistant />} />
          <Route path="settings" element={<Settings />} />
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </>
  );
}
