import { useState } from "react";
import Sidebar from "./Sidebar";
import AppHeader from "./AppHeader";
import "../../styles/app-shell.css";

export default function AppShell({ activePage = "medicines", title, subtitle, children }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="pharvo-shell">
      <Sidebar
        activePage={activePage}
        mobileOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        onNavigate={() => setSidebarOpen(false)}
      />
      <div className="pharvo-main">
        <AppHeader title={title} subtitle={subtitle} onMenuClick={() => setSidebarOpen(true)} />
        <main className="pharvo-content">{children}</main>
      </div>
    </div>
  );
}
