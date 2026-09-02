import { useEffect } from "react";
import Login from "./pages/auth/Login";
import Signup from "./pages/auth/Signup";
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

  return <RedirectTo to={roleHomePath(role)} />;
}
