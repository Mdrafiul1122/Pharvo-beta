"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { api } from "@/lib/api"
import Sidebar from "@/components/Sidebar"
import type { Product, Sale } from "@/types"

export default function DashboardPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [recentSales, setRecentSales] = useState<Sale[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.push("/login"); return }
    Promise.all([
      api.get<Product[]>("/inventory/products/"),
      api.get<Sale[]>("/sales/sales/"),
    ]).then(([p, s]) => {
      setProducts(p)
      const sorted = (Array.isArray(s) ? s : []).sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      setRecentSales(sorted.slice(0, 5))
    }).finally(() => setLoading(false))
  }, [user, isLoading, router])

  if (isLoading || !user) return null

  const totalProducts = products.length
  const lowStock = products.filter((p) => p.stock_quantity <= p.reorder_level).length
  const totalSales = recentSales.length

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Dashboard</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500">Total Products</p>
            <p className="text-3xl font-bold text-gray-800 mt-1">{totalProducts}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500">Low Stock Items</p>
            <p className="text-3xl font-bold text-orange-600 mt-1">{lowStock}</p>
          </div>
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <p className="text-sm text-gray-500">Recent Sales</p>
            <p className="text-3xl font-bold text-green-600 mt-1">{totalSales}</p>
          </div>
        </div>
        <div className="bg-white rounded-xl border border-gray-200 p-5">
          <h3 className="text-lg font-medium text-gray-800 mb-3">Recent Sales</h3>
          {loading ? (
            <p className="text-gray-400">Loading...</p>
          ) : recentSales.length === 0 ? (
            <p className="text-gray-400">No sales yet</p>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Invoice</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Customer</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Amount</th>
                  <th className="text-left py-2 px-3 text-gray-500 font-medium">Payment</th>
                </tr>
              </thead>
              <tbody>
                {recentSales.map((sale) => (
                  <tr key={sale.id} className="border-b border-gray-100">
                    <td className="py-2 px-3">{sale.invoice_number}</td>
                    <td className="py-2 px-3">{sale.customer_name || "Walk-in"}</td>
                    <td className="py-2 px-3">{sale.payable_amount}</td>
                    <td className="py-2 px-3">{sale.payment_method}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </main>
    </div>
  )
}
