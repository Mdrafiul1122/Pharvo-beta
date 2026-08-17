/**
 * Dashboard API service.
 *
 * Fetches the PHARVO dashboard summary using the JWT access token stored by
 * the authentication service (`services/auth.js`). The `/api` prefix is
 * proxied to the Django backend in development via `vite.config.js`.
 */

import { ApiError, getAccessToken } from "./auth";

const API_BASE = import.meta.env.VITE_API_URL ?? "/api";

/**
 * Fetch the dashboard summary for a given lookback period.
 *
 * @param {number} days - 7, 30 or 90
 * @returns {Promise<object>} dashboard payload from GET /api/dashboard/
 * @throws {ApiError} on failure; status 401 means the session expired
 */
export async function fetchDashboard(days = 30) {
  const token = getAccessToken();
  if (!token) {
    throw new ApiError("Authentication required. Please sign in.", 401);
  }

  let response;
  try {
    response = await fetch(`${API_BASE}/dashboard/?days=${days}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
  } catch (err) {
    throw new ApiError("Unable to connect to the dashboard service. Please try again.");
  }

  if (response.status === 401) {
    throw new ApiError("Your session has expired. Please sign in again.", 401);
  }

  if (!response.ok) {
    throw new ApiError("Unable to load dashboard data.", response.status);
  }

  return response.json();
}