import http from './http'
import type { DashboardResponse } from '@/types'

export const dashboardApi = {
  get: (params?: { start_date?: string; end_date?: string }) =>
    http.get<any, { data: DashboardResponse }>('/dashboard', { params }),
}
