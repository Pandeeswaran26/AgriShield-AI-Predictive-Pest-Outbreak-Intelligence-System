import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-field-950 text-mist">
      <Navbar />
      <Outlet />
    </div>
  );
}
