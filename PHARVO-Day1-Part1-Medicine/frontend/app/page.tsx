"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

export default function Home() {
  const router = useRouter()
  const { user, isLoading } = useAuth()

  useEffect(() => {
    if (isLoading) return
    if (user) router.replace("/dashboard")
    else router.replace("/login")
  }, [user, isLoading, router])

  return (
    <div className="flex items-center justify-center h-screen">
      <p className="text-gray-400">Loading...</p>
    </div>
  )
}
