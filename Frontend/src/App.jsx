import Dashboard from "./pages/Dashboard";
import MedicineSpecialistLogin from "./pages/MedicineSpecialistLogin";
import { getAccessToken } from "./services/auth";

export default function App() {
  const path = window.location.pathname;
  const authenticated = Boolean(getAccessToken());

  const showDashboard = path === "/dashboard" || (path === "/" && authenticated);

  return showDashboard ? <Dashboard /> : <MedicineSpecialistLogin />;
}