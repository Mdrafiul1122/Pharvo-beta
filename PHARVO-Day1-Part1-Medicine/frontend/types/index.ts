export interface Category {
  id: number
  name: string
  description: string
}

export interface Supplier {
  id: number
  name: string
  contact_person: string
  phone: string
  email: string
  address: string
  created_at: string
}

export interface Product {
  id: number
  name: string
  category: number
  category_name: string
  supplier: number | null
  supplier_name: string
  brand: string
  barcode: string
  unit_price: string
  cost_price: string
  stock_quantity: number
  reorder_level: number
  expiry_date: string | null
  is_active: boolean
  description: string
  created_at: string
  updated_at: string
}

export interface Customer {
  id: number
  name: string
  phone: string
  email: string
  address: string
  loyalty_points: number
  created_at: string
}

export interface Sale {
  id: number
  invoice_number: string
  customer: number | null
  customer_name: string | null
  user: number
  user_name: string
  total_amount: string
  discount: string
  payable_amount: string
  payment_method: "CASH" | "CARD" | "MOBILE"
  sale_date: string
  created_at: string
  items: SaleItem[]
}

export interface SaleItem {
  id: number
  sale: number
  product: number
  product_name: string
  quantity: number
  unit_price: string
  subtotal: string
}

export interface Purchase {
  id: number
  invoice_number: string
  supplier: number
  supplier_name: string
  user: number
  user_name: string
  total_amount: string
  discount: string
  payable_amount: string
  purchase_date: string
  created_at: string
  items: PurchaseItem[]
}

export interface PurchaseItem {
  id: number
  purchase: number
  product: number
  product_name: string
  quantity: number
  unit_price: string
  subtotal: string
  expiry_date: string | null
  manufactured_date: string | null
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
