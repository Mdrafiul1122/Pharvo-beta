import MedicineSpecialistLogin from "./pages/MedicineSpecialistLogin";
import Medicines from "./pages/Medicines";

export default function App() {
  const preview = new URLSearchParams(window.location.search).get("preview");

  // Temporary frontend-only preview route so the existing login remains the default.
  if (preview === "medicines") {
    return <Medicines />;
  }

  return <MedicineSpecialistLogin />;
}
