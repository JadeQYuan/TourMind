import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token') ?? sessionStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)

  // Role getters
  const isSystemAdmin = computed(() => user.value?.role === 'system_admin')
  const isAdmin = computed(() => user.value?.role === 'admin' || user.value?.role === 'system_admin')
  const isAssistant = computed(() => user.value?.role === 'assistant')

  function setToken(t: string, rememberMe: boolean) {
    token.value = t
    if (rememberMe) {
      localStorage.setItem('token', t)
      sessionStorage.removeItem('token')
    } else {
      sessionStorage.setItem('token', t)
      localStorage.removeItem('token')
    }
  }

  async function login(username: string, password: string, rememberMe = false) {
    const res = await authApi.login(username, password, rememberMe)
    if (res.code !== 0) throw new Error(res.message ?? '登录失败')
    setToken(res.data.access_token, rememberMe)
    // Fetch full user profile
    await fetchMe()
  }

  async function fetchMe() {
    const res = await authApi.me()
    user.value = res.data
  }

  function logout() {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    sessionStorage.removeItem('token')
  }

  return {
    token,
    user,
    isSystemAdmin,
    isAdmin,
    isAssistant,
    login,
    fetchMe,
    logout,
  }
})
