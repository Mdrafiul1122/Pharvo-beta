/**
 * Authentication service.
 *
 * Talks to the PHARVO backend API. No backend auth endpoint exists yet, so a
 * real request is sent to `/api/auth/login/` (proxied to Django in dev via
 * `vite.config.js`). When the endpoint is implemented, this module stays the
 * single integration point for JWT authentication.
 *
 * Override the API base with the `VITE_API_URL` environment variable.
 */

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

/**
 * Authenticate a user.
 *
 * @param {{ username: string, password: string, remember: boolean }} credentials
 * @returns {Promise<{ access?: string, refresh?: string }>} auth payload on success
 * @throws {ApiError} on failure with a user-facing message
 */
export async function loginUser({ username, password, remember }) {
  let response;

  try {
    response = await fetch(`${API_BASE}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",
      body: JSON.stringify({ username, password, remember }),
    });
  } catch (err) {
    throw new ApiError("Unable to connect to the authentication service. Please try again.");
  }

  const contentType = response.headers.get("content-type") ?? "";
  const isJson = contentType.includes("application/json");

  if (!response.ok) {
    if (isJson) {
      const data = await response.json().catch(() => ({}));
      throw new ApiError(
        data.detail || data.message || data.error || "Invalid username or password.",
        response.status
      );
    }
    throw new ApiError("Invalid username or password.", response.status);
  }

  if (!isJson) {
    // Defensive: a successful login must return JSON, never an HTML fallback.
    throw new ApiError("Unable to connect to the authentication service. Please try again.");
  }

  const data = await response.json().catch(() => ({}));

  // JWT-ready: persist tokens when the backend returns them.
  if (data.access) {
    localStorage.setItem("pharvo_access_token", data.access);
  }
  if (data.refresh) {
    localStorage.setItem("pharvo_refresh_token", data.refresh);
  }

  return data;
}
