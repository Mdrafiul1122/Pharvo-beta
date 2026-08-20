"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { api } from "@/lib/api"
import Sidebar from "@/components/Sidebar"
import DataTable from "@/components/DataTable"
import type { Purchase } from "@/types"

export default function PurchasesPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [purchases, setPurchases] = useState<Purchase[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.push("/login"); return }
    api.get<Purchase[]>("/purchases/purchases/")
      .then((d) => setPurchases(Array.isArray(d) ? d : []))
      .finally(() => setLoading(false))
  }, [user, isLoading, router])

  if (isLoading || !user) return null

  const columns = [
    { key: "invoice_number", label: "Invoice" },
    { key: "supplier_name", label: "Supplier" },
    { key: "payable_amount", label: "Amount", render: (p: Purchase) => `$${p.payable_amount}` },
    { key: "purchase_date", label: "Date" },
  ]

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-gray-800">Purchases</h2>
          <Link href="/purchases/new" className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700">
            + New Purchase
          </Link>
        </div>
        <div className="bg-white rounded-xl border border-gray-200">
          <DataTable columns={columns} data={purchases} loading={loading} />
        </div>
      </main>
    </div>
  )
}
