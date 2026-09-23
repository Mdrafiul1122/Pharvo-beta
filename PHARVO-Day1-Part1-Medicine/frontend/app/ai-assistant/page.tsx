"use client"

import { FormEvent, useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import Sidebar from "@/components/Sidebar"
import { api } from "@/lib/api"
import { useAuth } from "@/lib/auth-context"

interface MedicineMatch {
  medicine_id: number
  brand_name: string
  generic_name: string
  manufacturer: string
  strength: string
  dosage_form: string
  current_stock: number
  minimum_stock: number
  is_low_stock: boolean
  expiry_date: string
  pc_price: string
  strip_price: string
  box_price: string
}

interface InventoryMatch {
  candidate_generic: string
  available_medicines: MedicineMatch[]
}

interface AIResult {
  input_text: string
  normalized_query: string
  problem_id: string
  health_problem: string | null
  candidate_generics: string[]
  confidence: null
  requires_pharmacist_review: boolean
  inventory_matches?: InventoryMatch[]
}

export default function AIAssistantPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()

  const [query, setQuery] = useState("")
  const [result, setResult] = useState<AIResult | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState("")

  useEffect(() => {
    if (isLoading) return

    if (!user) {
      router.push("/login")
    }
  }, [user, isLoading, router])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!query.trim()) {
      setError("Please enter a customer complaint.")
      return
    }

    setSubmitting(true)
    setError("")
    setResult(null)

    try {
      const data = await api.post<AIResult>("/ai/query/", {
        text: query.trim(),
      })

      setResult(data)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to process the AI request."
      )
    } finally {
      setSubmitting(false)
    }
  }

  if (isLoading || !user) return null

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />

      <main className="flex-1 overflow-auto p-6">
        <div className="max-w-5xl mx-auto">
          <div className="mb-6">
            <h2 className="text-2xl font-semibold text-gray-800">
              AI Pharmacy Assistant
            </h2>

            <p className="text-sm text-gray-500 mt-1">
              Enter a complaint in Bangla, English, or Banglish.
              Results are decision support only and require pharmacist review.
            </p>
          </div>

          <form
            onSubmit={handleSubmit}
            className="bg-white border border-gray-200 rounded-xl p-5 mb-6"
          >
            <label
              htmlFor="complaint"
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Customer Complaint
            </label>

            <textarea
              id="complaint"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              rows={4}
              placeholder="Example: amar jor hoyeche"
              className="w-full rounded-lg border border-gray-300 px-3 py-3 text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />

            <button
              type="submit"
              disabled={submitting}
              className="mt-4 px-5 py-2.5 rounded-lg bg-blue-600 text-white text-sm font-medium hover:bg-blue-700 disabled:opacity-50"
            >
              {submitting ? "Analyzing..." : "Analyze Complaint"}
            </button>

            {error && (
              <div className="mt-4 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-700">
                {error}
              </div>
            )}
          </form>

          {result && (
            <div className="space-y-5">
              <div className="bg-white border border-gray-200 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  AI Classification
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p className="text-xs text-gray-500">
                      Problem ID
                    </p>
                    <p className="font-medium text-gray-800">
                      {result.problem_id}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-500">
                      Health Problem
                    </p>
                    <p className="font-medium text-gray-800">
                      {result.health_problem || "Unknown"}
                    </p>
                  </div>
                </div>

                <div className="mt-5">
                  <p className="text-sm text-gray-500 mb-2">
                    Candidate Generics
                  </p>

                  <div className="flex flex-wrap gap-2">
                    {result.candidate_generics.map((generic) => (
                      <span
                        key={generic}
                        className="px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm"
                      >
                        {generic}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-xl p-5">
                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                  Available Pharmacy Stock
                </h3>

                {!result.inventory_matches ||
                result.inventory_matches.every(
                  (item) => item.available_medicines.length === 0
                ) ? (
                  <p className="text-sm text-gray-500">
                    No matching in-stock, non-expired medicines found.
                  </p>
                ) : (
                  <div className="space-y-5">
                    {result.inventory_matches.map((group) => (
                      <div key={group.candidate_generic}>
                        <h4 className="font-medium text-gray-700 mb-2">
                          {group.candidate_generic}
                        </h4>

                        {group.available_medicines.length === 0 ? (
                          <p className="text-sm text-gray-400">
                            No available stock.
                          </p>
                        ) : (
                          <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                              <thead>
                                <tr className="border-b border-gray-200">
                                  <th className="text-left py-2 px-3 text-gray-500">
                                    Brand
                                  </th>
                                  <th className="text-left py-2 px-3 text-gray-500">
                                    Strength
                                  </th>
                                  <th className="text-left py-2 px-3 text-gray-500">
                                    Form
                                  </th>
                                  <th className="text-left py-2 px-3 text-gray-500">
                                    Stock
                                  </th>
                                  <th className="text-left py-2 px-3 text-gray-500">
                                    Expiry
                                  </th>
                                </tr>
                              </thead>

                              <tbody>
                                {group.available_medicines.map((medicine) => (
                                  <tr
                                    key={medicine.medicine_id}
                                    className="border-b border-gray-100"
                                  >
                                    <td className="py-3 px-3">
                                      <div className="font-medium text-gray-800">
                                        {medicine.brand_name}
                                      </div>

                                      <div className="text-xs text-gray-500">
                                        {medicine.manufacturer}
                                      </div>
                                    </td>

                                    <td className="py-3 px-3">
                                      {medicine.strength}
                                    </td>

                                    <td className="py-3 px-3">
                                      {medicine.dosage_form}
                                    </td>

                                    <td className="py-3 px-3">
                                      {medicine.current_stock}

                                      {medicine.is_low_stock && (
                                        <span className="ml-2 text-xs text-orange-600">
                                          Low
                                        </span>
                                      )}
                                    </td>

                                    <td className="py-3 px-3">
                                      {medicine.expiry_date}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
                <p className="font-medium text-amber-800">
                  Pharmacist Review Required
                </p>

                <p className="text-sm text-amber-700 mt-1">
                  This classifier does not provide a diagnosis or automatic
                  prescription. Candidate medicines must be reviewed by a
                  pharmacist before any dispensing decision.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}