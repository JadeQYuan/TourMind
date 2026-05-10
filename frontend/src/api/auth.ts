import http from './http'
import type { UserInfo } from '@/types'

export interface LoginUserInfo {
  id: number
  full_name: string
  role: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: LoginUserInfo
}

export const authApi = {
  login: (phone: string, password: string, rememberMe = false) =>
    http.post<any, { data: LoginResponse }>('/auth/login', {
      username: phone,
      password,
      remember_me: rememberMe,
    }),

  me: () => http.get<any, { data: UserInfo }>('/auth/me'),

  changePassword: (oldPassword: string, newPassword: string) =>
    http.post('/auth/change-password', {
      old_password: oldPassword,
      new_password: newPassword,
    }),

  logout: () => http.post('/auth/logout'),
}
