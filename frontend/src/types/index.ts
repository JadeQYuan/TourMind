// ── 用户 ───────────────────────────────────────────────────────────
export type UserRole = 'system_admin' | 'admin' | 'assistant'

export interface UserInfo {
  id: number
  name: string
  phone: string | null
  role: UserRole
  status: string
  last_login: string | null
  remark: string | null
  created_at: string
}

// ── 供应商 ─────────────────────────────────────────────────────────
export interface Supplier {
  id: number
  name: string
  contact_person: string | null
  contact_phone: string | null
  remark: string | null
  status: string
  created_at: string
}

// ── 账户 ───────────────────────────────────────────────────────────
export interface Account {
  id: number
  name: string
  type: string
  user_id: number | null
  user_name: string | null
  remark: string | null
  status: string
  created_at: string
  updated_at: string
}

// ── 产品 ───────────────────────────────────────────────────────────
export interface ProductTemplateDay {
  seq: number
  details: string
  accommodation_area?: string | null
  notes?: string | null
}

export interface Product {
  id: number
  name: string
  origin: string | null
  destination: string
  days: number
  price: number
  includes: string | null
  excludes: string | null
  cancellation_policy: string | null
  travel_notice: string | null
  important_tips: string | null
  itinerary_template: ProductTemplateDay[] | null
  remark: string | null
  status: string
  created_at: string
}

export type ProductListItem = Pick<Product, 'id' | 'name' | 'destination' | 'days' | 'price' | 'status' | 'created_at'>
export type ProductCreate = Omit<Product, 'id' | 'created_at'>
export type ProductUpdate = Partial<ProductCreate>

// ── 订单 ───────────────────────────────────────────────────────────
export type OrderStatus = 'pending_deposit' | 'pending_payment' | 'completed'

export interface Order {
  id: number
  order_no: string
  product_id: number | null
  customer_name: string
  customer_phone: string
  travel_date: string
  days: number
  people_count: number
  price: number
  deposit: number | null
  /** 定金到账日期，默认当前日期 */
  deposit_due_date: string | null
  /** 尾款金额，默认 price - deposit */
  balance_amount: number | null
  /** 尾款到账日期，默认行程结束日期 */
  balance_due_date: string | null
  supplier_id: number | null
  cost: number | null
  profit: number | null
  status: OrderStatus
  remarks: string | null
  user_id: number | null
  created_at: string
}

/** Alias: CustomerOrder is the primary order entity (same shape as Order) */
export type CustomerOrder = Order

export type OrderListItem = Order
export type OrderCreate = Omit<Order, 'id' | 'order_no' | 'profit' | 'created_at'>
export type OrderUpdate = Partial<OrderCreate>

// ── 行程 ───────────────────────────────────────────────────────────
interface ItineraryDayDetail {
  seq: number
  date?: string | null
  details: string
  accommodation_area?: string | null
  notes?: string | null
}

export interface Itinerary {
  id: number
  order_id: number
  order_no: string
  customer_order_id: number | null
  customer_name: string
  customer_phone: string
  destination: string
  pax: number
  travelers: string | null
  start_date: string
  end_date: string
  status: 'not_started' | 'in_progress' | 'completed' | 'cancelled'
  share_token: string | null
  days_detail: ItineraryDayDetail[]
  created_at: string
}

export type ItineraryListItem = Pick<Itinerary, 'id' | 'order_id' | 'order_no' | 'customer_order_id' | 'customer_name' | 'destination' | 'start_date' | 'end_date' | 'pax' | 'status' | 'share_token' | 'created_at'>
export type ItineraryCreate = Omit<Itinerary, 'id' | 'created_at'>
export type ItineraryUpdate = Partial<ItineraryCreate>

// ── 合同 ───────────────────────────────────────────────────────────
export interface Contract {
  id: number
  contract_no: string
  order_id: number
  order_no: string
  customer_order_id: number | null
  customer_name: string
  customer_phone: string
  pax: number
  travelers: Record<string, string>[] | null
  departure_date: string
  return_date: string
  total_amount: number
  price_per_person: number | null
  deposit_amount: number | null
  deposit_due_date: string | null
  balance_amount: number | null
  balance_due_date: string | null
  status: 'pending_sign' | 'signed' | 'revoked'
  cancel_reason: string | null
  share_token: string | null
  signature_url: string | null
  signature_image_url: string | null
  signed_at: string | null
  includes: string | null
  excludes: string | null
  travel_notice: string | null
  cancellation_policy: string | null
  notes: string | null
  bill_summary: { total_income: number; pending_income: number; total_expense: number; estimated_profit: number } | null
  days_detail: { day_number: number; date: string; details: string; accommodation_area?: string | null }[]
  created_at: string
  party_a?: string | null
  party_a_phone?: string | null
  party_b?: string | null
  party_b_phone?: string | null
}

export type ContractListItem = Pick<Contract, 'id' | 'contract_no' | 'order_id' | 'order_no' | 'customer_order_id' | 'customer_name' | 'status' | 'share_token' | 'signed_at' | 'created_at'>
export type ContractCreate = {
  customer_order_id: number
  includes?: string | null
  excludes?: string | null
  travel_notice?: string | null
  cancellation_policy?: string | null
  notes?: string | null
  party_a: string
  party_a_phone: string
  party_b: string
  party_b_phone: string
}
export type ContractUpdate = Partial<ContractCreate> & { customer_order_id: number }

// ── 账单 ───────────────────────────────────────────────────────────
export interface Bill {
  id: number
  customer_order_id: number | null
  order_id: number | null
  order_no: string | null
  bill_type: 'income' | 'expense'
  income_type: string | null
  expense_type: string | null
  amount: number
  account_id: number | null
  account_name: string | null
  bill_date: string
  notes: string | null
  attachment_url: string | null
  created_at: string
}

export type BillCreate = Omit<Bill, 'id' | 'created_at' | 'account_name' | 'order_no'>
export type BillUpdate = Partial<BillCreate>

// ── 看板 ───────────────────────────────────────────────────────────
export interface DashboardSummary {
  total_orders: number
  total_income: number
  total_expense: number
  total_profit: number
  period_start: string
  period_end: string
}

export interface OrderStatusDistributionItem {
  status: OrderStatus
  label: string
  count: number
}

export interface MonthlyTrendItem {
  month: string
  income: number
  expense: number
  profit: number
}

export interface TopProductItem {
  product_id: number | null
  product_name: string
  order_count: number
  total_income: number
}

export interface TopSupplierItem {
  supplier_id: number | null
  supplier_name: string
  order_count: number
  total_cost: number
}

export interface DashboardResponse {
  summary: DashboardSummary
  order_status_distribution: OrderStatusDistributionItem[]
  monthly_income_trend: MonthlyTrendItem[]
  top_products: TopProductItem[]
  top_suppliers: TopSupplierItem[]
  recent_orders: Partial<Order>[]
}

// ── 审计日志 ────────────────────────────────────────────────────────
export interface AuditLog {
  id: number
  user_id: number | null
  user_name: string | null
  action: string
  resource_type: string | null
  resource_id: string | null
  detail: string | null
  ip_address: string | null
  created_at: string
}

export interface AuditLogListResponse {
  total: number
  page: number
  page_size: number
  items: AuditLog[]
}
