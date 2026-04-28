import http from './http'

export const userApi = {
  list: (params?: object) => http.get('/users', { params }),
  get: (id: number) => http.get(`/users/${id}`),
  create: (data: object) => http.post('/users', data),
  update: (id: number, data: object) => http.put(`/users/${id}`, data),
  patchStatus: (id: number) => http.patch(`/users/${id}/status`),
  remove: (id: number) => http.delete(`/users/${id}`),
  resetPassword: (id: number) => http.post(`/users/${id}/reset-password`),
}
