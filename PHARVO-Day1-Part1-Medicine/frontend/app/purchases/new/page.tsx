"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { api } from "@/lib/api"
import Sidebar from "@/components/Sidebar"
import type { Product, Supplier } from "@/types"

let purchaseCounter = 0
function nextPurchaseInvoice() {
  purchaseCounter++
  return `PUR-${Date.now()}-${purchaseCounter}`
}

interface LineItem {
  product: number
  product_name: string
  quantity: number
  unit_price: string
  subtotal: string
}

export default function NewPurchasePage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [products, setProducts] = useState<Product[]>([])
  const [suppliers, setSuppliers] = useState<Supplier[]>([])
  const [supplierId, setSupplierId] = useState("")
  const [purchaseDate, setPurchaseDate] = useState(new Date().toISOString().split("T")[0])
  const [items, setItems] = useState<LineItem[]>([])
  const [selectedProduct, setSelectedProduct] = useState("")
  const [quantity, setQuantity] = useState(1)
  const [unitPrice, setUnitPrice] = useState("")
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.push("/login"); return }
    Promise.all([
      api.get<Product[]>("/inventory/products/"),
      api.get<Supplier[]>("/inventory/suppliers/"),
    ]).then(([p, s]) => {
      setProducts(Array.isArray(p) ? p : [])
      setSuppliers(Array.isArray(s) ? s : [])
    })
  }, [user, isLoading, router])

  function addItem() {
    if (!selectedProduct) return
    const product = products.find((p) => p.id === Number(selectedProduct))
    if (!product) return
    const price = unitPrice || product.cost_price
    const qty = Math.max(1, quantity)
    const subtotal = (Number(price) * qty).toFixed(2)
    setItems([...items, {
      product: product.id,
      product_name: product.name,
      quantity: qty,
      unit_price: price,
      subtotal,
    }])
    setSelectedProduct("")
    setQuantity(1)
    setUnitPrice("")
  }

  function removeItem(index: number) {
    setItems(items.filter((_, i) => i !== index))
  }

  const total = items.reduce((sum, item) => sum + Number(item.subtotal), 0)

  async function handleSubmit() {
    if (items.length === 0 || !supplierId) return
    setSaving(true)
    try {
      const invoiceNumber = nextPurchaseInvoice()
      await api.post("/purchases/purchases/", {
        invoice_number: invoiceNumber,
        supplier: Number(supplierId),
        total_amount: total.toFixed(2),
        discount: "0.00",
        payable_amount: total.toFixed(2),
        purchase_date: purchaseDate,
        items: items.map((item) => ({
          product: item.product,
          quantity: item.quantity,
          unit_price: item.unit_price,
          subtotal: item.subtotal,
        })),
      })
      router.push("/purchases")
    } catch (err) {
      alert("Purchase failed: " + err)
    } finally {
      setSaving(false)
    }
  }

  if (isLoading || !user) return null

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">New Purchase</h2>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-4">
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <h3 className="font-medium text-gray-700 mb-3">Add Items</h3>
              <div className="grid grid-cols-4 gap-2">
                <select
                  value={selectedProduct}
                  onChange={(e) => {
                    setSelectedProduct(e.target.value)
                    const p = products.find((pr) => pr.id === Number(e.target.value))
                    if (p) setUnitPrice(p.cost_price)
                  }}
                  className="col-span-2 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Select product --</option>
                  {products.map((p) => (
                    <option key={p.id} value={p.id}>{p.name}</option>
                  ))}
                </select>
                <input
                  type="number" min="1" value={quantity}
                  onChange={(e) => setQuantity(Number(e.target.value))}
                  placeholder="Qty"
                  className="px-3 py-2 border border-gray-300 rounded-lg text-sm text-center focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <div className="flex gap-2">
                  <input
                    type="number" step="0.01" value={unitPrice}
                    onChange={(e) => setUnitPrice(e.target.value)}
                    placeholder="Price"
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button onClick={addItem} className="px-3 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 whitespace-nowrap">
                    Add
                  </button>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200">
              {items.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No items added</p>
              ) : (
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 text-gray-500 font-medium">Product</th>
                      <th className="text-center py-3 px-4 text-gray-500 font-medium">Qty</th>
                      <th className="text-right py-3 px-4 text-gray-500 font-medium">Unit Price</th>
                      <th className="text-right py-3 px-4 text-gray-500 font-medium">Subtotal</th>
                      <th></th>
                    </tr>
                  </thead>
                  <tbody>
                    {items.map((item, i) => (
                      <tr key={i} className="border-b border-gray-100">
                        <td className="py-3 px-4">{item.product_name}</td>
                        <td className="py-3 px-4 text-center">{item.quantity}</td>
                        <td className="py-3 px-4 text-right">${item.unit_price}</td>
                        <td className="py-3 px-4 text-right font-medium">${item.subtotal}</td>
                        <td className="py-3 px-4 text-right">
                          <button onClick={() => removeItem(i)} className="text-red-500 text-xs">Remove</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>

          <div className="space-y-4">
            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <h3 className="font-medium text-gray-700 mb-3">Purchase Details</h3>
              <div className="space-y-3">
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Supplier *</label>
                  <select value={supplierId} onChange={(e) => setSupplierId(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                    <option value="">-- Select --</option>
                    {suppliers.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-600 mb-1">Date</label>
                  <input type="date" value={purchaseDate} onChange={(e) => setPurchaseDate(e.target.value)} className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl border border-gray-200 p-4">
              <div className="flex justify-between items-center mb-4">
                <span className="text-gray-600">Items</span>
                <span className="font-medium">{items.length}</span>
              </div>
              <div className="flex justify-between items-center mb-4 text-lg">
                <span className="font-semibold text-gray-800">Total</span>
                <span className="font-bold text-gray-900">${total.toFixed(2)}</span>
              </div>
              <button
                onClick={handleSubmit}
                disabled={items.length === 0 || !supplierId || saving}
                className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50"
              >
                {saving ? "Processing..." : "Complete Purchase"}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
