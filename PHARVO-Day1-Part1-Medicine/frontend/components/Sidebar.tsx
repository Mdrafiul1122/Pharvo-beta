"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { useAuth } from "@/lib/auth-context"

const links = [
  { href: "/dashboard", label: "Dashboard", icon: "📊" },
  { href: "/products", label: "Products", icon: "💊" },
  { href: "/categories", label: "Categories", icon: "📂" },
  { href: "/suppliers", label: "Suppliers", icon: "🏭" },
  { href: "/customers", label: "Customers", icon: "👤" },
  { href: "/sales", label: "Sales", icon: "🧾" },
  { href: "/purchases", label: "Purchases", icon: "📦" },
]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAuth()

  return (
    <aside className="w-60 min-h-screen bg-white border-r border-gray-200 flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-lg font-bold text-gray-800">Sheba Pharmacy</h1>
        <p className="text-sm text-gray-500">POS System</p>
      </div>
      <nav className="flex-1 p-2 space-y-1">
        {links.map((link) => {
          const active = pathname.startsWith(link.href)
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                active
                  ? "bg-blue-50 text-blue-700 font-medium"
                  : "text-gray-600 hover:bg-gray-50"
              }`}
            >
              <span>{link.icon}</span>
              {link.label}
            </Link>
          )
        })}
      </nav>
      <div className="p-4 border-t border-gray-200">
        <p className="text-sm text-gray-600 truncate">{user?.username}</p>
        <button
          onClick={logout}
          className="text-sm text-red-500 hover:text-red-700 mt-1"
        >
          Logout
        </button>
      </div>
    </aside>
  )
}
