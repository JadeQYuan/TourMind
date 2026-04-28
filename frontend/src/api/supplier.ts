import http from './http'
import type { Supplier } from '@/types'

export const supplierApi = {
  list: (params?: Record<string, unknown>) =>
    http.get<any, { data: Supplier[] }>('/suppliers', { params }),

  get: (id: number) =>
    http.get<any, { data: Supplier }>(`/suppliers/${id}`),

  create: (data: Partial<Supplier>) =>
    http.post<any, { data: Supplier }>('/suppliers', data),

  update: (id: number, data: Partial<Supplier>) =>
    http.put(`/suppliers/${id}`, data),

  delete: (id: number) =>
    http.delete(`/suppliers/${id}`),
}
