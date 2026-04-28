import http from './http'
import type { Bill, BillCreate, BillUpdate, DashboardSummary } from '@/types'

export interface BillListParams {
  bill_type?: string
  contract_id?: number
  customer_order_id?: number
  account_id?: number
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}

export const billApi = {
  summary: () =>
    http.get<any, { data: DashboardSummary }>('/bills/summary'),

  list: (params?: BillListParams) =>
    http.get<any, { data: { items: Bill[]; total: number } | Bill[] }>('/bills', { params }),

  get: (id: number) =>
    http.get<any, { data: Bill }>(`/bills/${id}`),

  create: (data: BillCreate) =>
    http.post<any, { data: Bill }>('/bills', data),

  update: (id: number, data: BillUpdate) =>
    http.put(`/bills/${id}`, data),

  delete: (id: number) =>
    http.delete(`/bills/${id}`),
}
