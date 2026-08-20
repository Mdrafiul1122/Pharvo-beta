"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { api } from "@/lib/api"
import Sidebar from "@/components/Sidebar"
import DataTable from "@/components/DataTable"
import type { Customer } from "@/types"

export default function CustomersPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [customers, setCustomers] = useState<Customer[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.push("/login"); return }
    api.get<Customer[]>("/customers/customers/")
      .then((d) => setCustomers(Array.isArray(d) ? d : []))
      .finally(() => setLoading(false))
  }, [user, isLoading, router])

  if (isLoading || !user) return null

  const columns = [
    { key: "name", label: "Name" },
    { key: "phone", label: "Phone" },
    { key: "email", label: "Email" },
    { key: "loyalty_points", label: "Points" },
  ]

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Customers</h2>
        <div className="bg-white rounded-xl border border-gray-200">
          <DataTable columns={columns} data={customers} loading={loading} />
        </div>
      </main>
    </div>
  )
}
