import http from './http'
import type { Contract, ContractListItem, ContractCreate, ContractUpdate } from '@/types'

export const contractApi = {
  list: (params?: Record<string, unknown>) =>
    http.get<any, { data: { items: ContractListItem[]; total: number } | ContractListItem[] }>('/contracts', { params }),

  get: (id: number) =>
    http.get<any, { data: Contract }>(`/contracts/${id}`),

  create: (data: ContractCreate) => {
    // 前端类型校验，确保必填字段存在
    if (!data.customer_order_id || !data.party_a || !data.party_a_phone || !data.party_b || !data.party_b_phone) {
      throw new Error('创建合同缺少必填字段')
    }
    return http.post<any, { data: ContractListItem }>('/contracts', data)
  },

  update: (id: number, data: ContractUpdate) => {
    // 前端类型校验，确保必填字段存在
    if (!data.customer_order_id || !data.party_a || !data.party_a_phone || !data.party_b || !data.party_b_phone) {
      throw new Error('更新合同缺少必填字段')
    }
    return http.put(`/contracts/${id}`, data)
  },

  updateStatus: (id: number, status: string, cancelReason?: string) =>
    http.patch<any, { data: { status: string } }>(
      `/contracts/${id}/status`,
      { status, cancel_reason: cancelReason },
    ),

  share: (id: number) =>
    http.post<any, { data: { message: string } }>(`/contracts/${id}/share`),

  revokeShare: (id: number) =>
    http.delete(`/contracts/${id}/share`),

  delete: (id: number) =>
    http.delete(`/contracts/${id}`),
}

export const publicContractApi = {
  getByToken: (token: string) =>
    http.get<any, { data: Contract }>(`/public/contracts/${token}`),

  verifyPhone: (token: string, phone: string) =>
    http.post<any, { data: { verified: boolean } }>(`/public/contracts/${token}/verify-phone`, { phone }),

  sign: (token: string, signatureImageUrl: string, idDocuments: unknown[]) =>
    http.post(`/public/contracts/${token}/sign`, {
      signature_image_url: signatureImageUrl,
      id_documents: idDocuments,
    }),
}
