import http from './http'
import type { OrderListItem, OrderCreate, OrderUpdate } from '@/types'

export const orderApi = {
  list: (params?: Record<string, unknown>) =>
    http.get<any, { data: { items: OrderListItem[]; total: number } | OrderListItem[] }>('/orders', { params }),

  get: (id: number) =>
    http.get<any, { data: OrderListItem }>(`/orders/${id}`),

  create: (data: OrderCreate) =>
    http.post<any, { data: OrderListItem }>('/orders', data),

  update: (id: number, data: OrderUpdate) =>
    http.put<any, { data: OrderListItem }>(`/orders/${id}`, data),

  updateStatus: (id: number, status: string) =>
    http.patch(`/orders/${id}/status`, { status }),

  delete: (id: number) =>
    http.delete(`/orders/${id}`),
}
