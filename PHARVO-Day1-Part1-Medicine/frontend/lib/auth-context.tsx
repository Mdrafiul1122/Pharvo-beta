"use client"

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import { api } from "./api"

interface User {
  id: number
  username: string
  is_staff: boolean
}

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

function parseJwt(token: string): User | null {
  try {
    const base64Url = token.split(".")[1]
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/")
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    )
    const payload = JSON.parse(jsonPayload)
    return {
      id: payload.user_id,
      username: payload.username,
      is_staff: payload.is_staff || false,
    }
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [hydrated, setHydrated] = useState(false)
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    const token = localStorage.getItem("access_token")
    if (token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      setUser(parseJwt(token))
    }
    setHydrated(true)
  }, [])

  const login = useCallback(async (username: string, password: string) => {
    const data = await api.post<{ access: string; refresh: string }>("/auth/token/", {
      username,
      password,
    })
    localStorage.setItem("access_token", data.access)
    localStorage.setItem("refresh_token", data.refresh)
    setUser(parseJwt(data.access))
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    setUser(null)
    window.location.href = "/login"
  }, [])

  return (
    <AuthContext.Provider value={{ user, isLoading: !hydrated, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
