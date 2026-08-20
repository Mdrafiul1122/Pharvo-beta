"use client"

import { useEffect, useState, type FormEvent } from "react"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { api } from "@/lib/api"
import Sidebar from "@/components/Sidebar"
import DataTable from "@/components/DataTable"
import type { Category } from "@/types"

export default function CategoriesPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [newName, setNewName] = useState("")
  const [adding, setAdding] = useState(false)

  function load() {
    api.get<Category[]>("/inventory/categories/")
      .then((d) => setCategories(Array.isArray(d) ? d : []))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    if (isLoading) return
    if (!user) { router.push("/login"); return }
    load()
  }, [user, isLoading, router])

  async function handleAdd(e: FormEvent) {
    e.preventDefault()
    if (!newName.trim()) return
    setAdding(true)
    try {
      await api.post("/inventory/categories/", { name: newName })
      setNewName("")
      load()
    } catch (err) {
      alert("Failed: " + err)
    } finally {
      setAdding(false)
    }
  }

  async function handleDelete(cat: Category) {
    if (!confirm(`Delete "${cat.name}"?`)) return
    try {
      await api.delete(`/inventory/categories/${cat.id}/`)
      load()
    } catch {
      alert("Cannot delete category with existing products")
    }
  }

  if (isLoading || !user) return null

  const columns = [
    { key: "name", label: "Name" },
    { key: "description", label: "Description" },
  ]

  return (
    <div className="flex h-screen">
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">
        <h2 className="text-2xl font-semibold text-gray-800 mb-6">Categories</h2>
        <form onSubmit={handleAdd} className="flex gap-2 mb-6">
          <input
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="New category name"
            className="flex-1 max-w-xs px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <button type="submit" disabled={adding} className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 disabled:opacity-50">
            {adding ? "..." : "Add"}
          </button>
        </form>
        <div className="bg-white rounded-xl border border-gray-200">
          <DataTable columns={columns} data={categories} loading={loading} onDelete={handleDelete} />
        </div>
      </main>
    </div>
  )
}
