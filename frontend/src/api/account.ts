import http from './http'
import type { Account } from '@/types'

export const accountApi = {
  list: (params?: Record<string, unknown>) =>
    http.get<any, { data: Account[] }>('/accounts', { params }),

  get: (id: number) =>
    http.get<any, { data: Account }>(`/accounts/${id}`),

  create: (data: Partial<Account>) =>
    http.post<any, { data: Account }>('/accounts', data),

  update: (id: number, data: Partial<Account>) =>
    http.put(`/accounts/${id}`, data),

  delete: (id: number) =>
    http.delete(`/accounts/${id}`),
}
