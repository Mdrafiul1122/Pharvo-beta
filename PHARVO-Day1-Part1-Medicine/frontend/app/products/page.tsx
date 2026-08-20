"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "@/lib/auth-context"
import { api } from "@/lib/api"
import Sidebar from "@/components/Sidebar"
import DataTable from "@/components/DataTable"
import type { Product } from "@/types"

export default function ProductsPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.push("/login"); return }
    api.get<Product[]>("/inventory/products/")
      .then(setProducts)
      .finally(() => setLoading(false))
  }, [user, isLoading, router])

  if (isLoading || !user) return null

  const columns = [
    { key: "name", label: "Name" },
    { key: "category_name", label: "Category" },
    {
      key: "unit_price", label: "Price",
      render: (p: Product) => `$${p.unit_price}`,
    },
    { key: "stock_quantity", label: "Stock" },
    {
      key: "status", label: "Status",
      render: (p: Product) =>
        p.stock_quantity <= p.reorder_level ? (
          <span className="text-red-600 font-medium">Low</span>
        ) : (
          <span className="text-green-600">OK</span>
        ),
    },
  ]

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-semibold text-gray-800">Products</h2>
          <Link
            href="/products/new"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700"
          >
            + New Product
          </Link>
        </div>
        <div className="bg-white rounded-xl border border-gray-200">
          <DataTable columns={columns} data={products} loading={loading} />
        </div>
      </main>
    </div>
  )
}
