import http from './http'
import type { Product, ProductListItem, ProductCreate } from '@/types'

export interface ProductListParams {
  keyword?: string
  product_type?: string
  status?: string
  page?: number
  page_size?: number
}

export const productApi = {
  list: (params?: ProductListParams) =>
    http.get<never, { data: { items: ProductListItem[]; total: number } | ProductListItem[] }>('/products', { params }),
  get: (id: number) =>
    http.get<never, { data: Product }>(`/products/${id}`),
  create: (data: ProductCreate) =>
    http.post<never, { data: Product }>('/products', data),
  update: (id: number, data: Partial<ProductCreate>) =>
    http.put<never, { data: Product }>(`/products/${id}`, data),
  copy: (id: number) =>
    http.post<never, { data: Product }>(`/products/${id}/copy`),
  delete: (id: number) =>
    http.delete(`/products/${id}`),
}
