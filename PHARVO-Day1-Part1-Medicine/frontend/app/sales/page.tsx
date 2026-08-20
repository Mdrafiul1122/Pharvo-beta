"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { api } from "@/lib/api"
import Sidebar from "@/components/Sidebar"
import DataTable from "@/components/DataTable"
import type { Sale } from "@/types"

export default function SalesPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [sales, setSales] = useState<Sale[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.push("/login"); return }
    api.get<Sale[]>("/sales/sales/")
      .then((d) => setSales(Array.isArray(d) ? d : []))
      .finally(() => setLoading(false))
  }, [user, isLoading, router])

  if (isLoading || !user) return null

  const columns = [
    { key: "invoice_number", label: "Invoice" },
    { key: "customer_name", label: "Customer", render: (s: Sale) => s.customer_name || "Walk-in" },
    { key: "payable_amount", label: "Amount", render: (s: Sale) => `$${s.payable_amount}` },
    { key: "payment_method", label: "Payment" },
    { key: "sale_date", label: "Date" },
  ]

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-gray-800">Sales</h2>
          <Link href="/sales/new" className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm hover:bg-green-700">
            + New Sale
          </Link>
        </div>
        <div className="bg-white rounded-xl border border-gray-200">
          <DataTable columns={columns} data={sales} loading={loading} />
        </div>
      </main>
    </div>
  )
}
