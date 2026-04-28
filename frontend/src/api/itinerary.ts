import http from './http'
import type { Itinerary, ItineraryListItem, ItineraryCreate, ItineraryUpdate, Order, OrderCreate, OrderUpdate } from '@/types'

export const itineraryApi = {
  list: (params?: Record<string, unknown>) =>
    http.get<any, { data: ItineraryListItem[] }>('/itineraries', { params }),

  get: (id: number) =>
    http.get<any, { data: Itinerary }>(`/itineraries/${id}`),

  create: (data: ItineraryCreate) =>
    http.post<any, { data: Itinerary }>('/itineraries', data),

  update: (id: number, data: ItineraryUpdate) =>
    http.put<any, { data: Itinerary }>(`/itineraries/${id}`, data),

  patchStatus: (id: number, status: string) =>
    http.patch(`/itineraries/${id}/status`, { status }),

  getPublicItinerary: (token: string) =>
http.get<any, { data: Itinerary }>(`/public/itineraries/${token}`),

  copy: (id: number) =>
    http.post<any, { data: { id: number } }>(`/itineraries/${id}/copy`),

  delete: (id: number) =>
    http.delete(`/itineraries/${id}`),

  // 供应商子订单
  listOrders: (itineraryId: number) =>
    http.get<any, { data: Order[] }>(`/itineraries/${itineraryId}/orders`),

  createOrder: (itineraryId: number, data: OrderCreate) =>
    http.post<any, { data: Order }>(`/itineraries/${itineraryId}/orders`, data),

  updateOrder: (itineraryId: number, orderId: number, data: OrderUpdate) =>
    http.put<any, { data: Order }>(`/itineraries/${itineraryId}/orders/${orderId}`, data),

  deleteOrder: (itineraryId: number, orderId: number) =>
    http.delete(`/itineraries/${itineraryId}/orders/${orderId}`),
}
