const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

async function refreshToken(): Promise<string | null> {
  const refresh = localStorage.getItem("refresh_token")
  if (!refresh) return null
  const res = await fetch(`${API_BASE}/auth/token/refresh/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  })
  if (!res.ok) {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    return null
  }
  const data = await res.json()
  localStorage.setItem("access_token", data.access)
  return data.access
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = localStorage.getItem("access_token")
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers["Authorization"] = `Bearer ${token}`
  }

  let res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers })

  if (res.status === 401) {
    const newToken = await refreshToken()
    if (newToken) {
      headers["Authorization"] = `Bearer ${newToken}`
      res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers })
    } else {
      window.location.href = "/login"
      throw new Error("Session expired")
    }
  }

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Request failed: ${res.status}`)
  }

  if (res.status === 204) return undefined as T
  return res.json()
}

export const api = {
  get: <T>(url: string) => request<T>(url),
  post: <T>(url: string, data: unknown) =>
    request<T>(url, { method: "POST", body: JSON.stringify(data) }),
  put: <T>(url: string, data: unknown) =>
    request<T>(url, { method: "PUT", body: JSON.stringify(data) }),
  patch: <T>(url: string, data: unknown) =>
    request<T>(url, { method: "PATCH", body: JSON.stringify(data) }),
  delete: <T>(url: string) =>
    request<T>(url, { method: "DELETE" }),
}
