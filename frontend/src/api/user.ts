import http from './http'

export const userApi = {
  list: (params?: object) => http.get('/users', { params }),
  get: (id: number) => http.get(`/users/${id}`),
  create: (data: { name: string; phone: string; role: string; password: string }) => http.post('/users', data),
  update: (id: number, data: { name?: string; phone?: string; role?: string }) => http.put(`/users/${id}`, data),
  patchStatus: (id: number) => http.patch(`/users/${id}/status`),
  remove: (id: number) => http.delete(`/users/${id}`),
  resetPassword: (id: number, password: string) => http.post(`/users/${id}/reset-password`, { password }),
}
