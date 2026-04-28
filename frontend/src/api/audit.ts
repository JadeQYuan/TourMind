import http from './http'
import type { AuditLog, AuditLogListResponse } from '@/types'

export interface AuditLogParams {
  keyword?: string
  user_id?: number
  result?: string
  page?: number
  page_size?: number
}

export const auditApi = {
  list: (params?: AuditLogParams) =>
    http.get<any, { data: AuditLogListResponse }>('/audit-logs', { params }),
}
