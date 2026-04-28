import type { MockMethod } from 'vite-plugin-mock'
import { ok, MOCK_ORDERS, MOCK_BILLS } from './_data'

const DATA_REF_DATE = new Date('2026-04-16')

function monthlyTrend() {
  const now = DATA_REF_DATE
  const result: { month: string; income: number; expense: number; profit: number }[] = []
  for (let i = 5; i >= 0; i--) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1)
    const key = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    const monthBills = MOCK_BILLS.filter(b => b.bill_date.startsWith(key))
    const income = monthBills.filter(b => b.bill_type === 'income').reduce((s, b) => s + b.amount, 0)
    const expense = monthBills.filter(b => b.bill_type === 'expense').reduce((s, b) => s + b.amount, 0)
    result.push({ month: key, income, expense, profit: income - expense })
  }
  return result
}

export default [
  {
    url: '/api/v1/dashboard',
    method: 'get',
    response: () => {
      const orders = MOCK_ORDERS
      const bills = MOCK_BILLS

      const totalIncome = bills.filter(b => b.bill_type === 'income').reduce((s, b) => s + b.amount, 0)
      const totalExpense = bills.filter(b => b.bill_type === 'expense').reduce((s, b) => s + b.amount, 0)

      // Order status distribution
      const statusMap = new Map<string, number>()
      for (const o of orders) {
        statusMap.set(o.status, (statusMap.get(o.status) ?? 0) + 1)
      }
      const orderStatusDistribution = Array.from(statusMap.entries()).map(([status, count]) => ({ status, count }))

      // Top products by order count
      const productMap = new Map<string, number>()
      for (const o of orders) {
        const k = o.product_name ?? '未知'
        productMap.set(k, (productMap.get(k) ?? 0) + 1)
      }
      const topProducts = Array.from(productMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([product_name, order_count]) => ({ product_name, order_count }))

      // Top suppliers by cost
      const supplierMap = new Map<string, number>()
      for (const o of orders) {
        const k = o.supplier_name ?? '未知'
        supplierMap.set(k, (supplierMap.get(k) ?? 0) + (o.cost ?? 0))
      }
      const topSuppliers = Array.from(supplierMap.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([supplier_name, total_cost]) => ({ supplier_name, total_cost }))

      // Recent orders (last 5)
      const recentOrders = [...orders]
        .sort((a, b) => b.created_at.localeCompare(a.created_at))
        .slice(0, 5)
        .map(o => ({
          id: o.id,
          order_no: o.order_no,
          customer_name: o.customer_name,
          product_name: o.product_name,
          total_price: o.total_price,
          status: o.status,
        }))

      return ok({
        summary: {
          total_orders: orders.length,
          total_income: totalIncome,
          total_expense: totalExpense,
          total_profit: totalIncome - totalExpense,
        },
        order_status_distribution: orderStatusDistribution,
        monthly_income_trend: monthlyTrend(),
        top_products: topProducts,
        top_suppliers: topSuppliers,
        recent_orders: recentOrders,
      })
    },
  },
] as MockMethod[]

