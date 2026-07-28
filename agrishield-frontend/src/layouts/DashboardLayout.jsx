import { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";
import AssistantWidget from "../components/common/AssistantWidget";

const TITLES = {
  "/dashboard": "Dashboard",
  "/predict": "AI Prediction",
  "/recommendation": "AI Recommendation",
  "/history": "Prediction History",
  "/analytics": "Analytics",
  "/settings": "Settings",
};

export default function DashboardLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { pathname } = useLocation();

  return (
    <div className="flex min-h-screen bg-surface-muted dark:bg-surface-dark">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      <div className="flex min-h-screen flex-1 flex-col">
        <Topbar
          title={TITLES[pathname] || "AgriShield AI"}
          onMenuClick={() => setSidebarOpen(true)}
        />
        <main className="flex-1 p-4 sm:p-8">
          <Outlet />
        </main>
      </div>

      <AssistantWidget />
    </div>
  );
}
