import { useEffect } from "react";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
import AdminDashboard from "./pages/dashboard/AdminDashboard";
import CustomerPortal from "./pages/dashboard/CustomerPortal";
import {
  clearStoredTokens,
  getAccessToken,
  getStoredRole,
  roleHomePath,
} from "./services/auth";

function RedirectTo({ to }) {
  useEffect(() => {
    window.location.assign(to);
  }, [to]);
  return null;
}

function RoleRoute({ path, role, children }) {
  const currentPath = window.location.pathname;
  if (currentPath !== path) {
    return null;
  }
  if (getStoredRole() !== role) {
    return <RedirectTo to={roleHomePath(getStoredRole())} />;
  }
  return children;
}

export default function App() {
  const path = window.location.pathname;
  const authenticated = Boolean(getAccessToken());
  const role = getStoredRole();

  if (authenticated && !role) {
    // Token without a cached user: treat as an invalid session.
    clearStoredTokens();
    return path === "/signup" ? <Signup /> : <Login />;
  }

  if (!authenticated) {
    return path === "/signup" ? <Signup /> : <Login />;
  }

  const home = roleHomePath(role);

  if (path === "/" || path === "/signup") {
    return <RedirectTo to={home} />;
  }

  return (
    <>
      <RoleRoute path="/admin/dashboard" role="admin">
        <AdminDashboard />
      </RoleRoute>
      <RoleRoute path="/pharmacist/dashboard" role="pharmacist">
        <Dashboard />
      </RoleRoute>
      <RoleRoute path="/customer/portal" role="customer">
        <CustomerPortal />
      </RoleRoute>
      {path !== "/admin/dashboard" &&
        path !== "/pharmacist/dashboard" &&
        path !== "/customer/portal" && <RedirectTo to={home} />}
    </>
  );
}