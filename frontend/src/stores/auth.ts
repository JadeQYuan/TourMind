import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { UserInfo } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token') ?? sessionStorage.getItem('token'))
  const user = ref<UserInfo | null>(null)
  const must_change_password = ref(false)

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
    must_change_password.value = res.data.user.must_change_password
    // Fetch full user profile
    await fetchMe()
    return { must_change_password: must_change_password.value }
  }

  async function fetchMe() {
    const res = await authApi.me()
    user.value = res.data
    if (res.data && 'must_change_password' in res.data) {
      must_change_password.value = (res.data as any).must_change_password ?? false
    }
  }

  function logout() {
    token.value = null
    user.value = null
    must_change_password.value = false
    localStorage.removeItem('token')
    sessionStorage.removeItem('token')
  }

  return {
    token,
    user,
    must_change_password,
    isSystemAdmin,
    isAdmin,
    isAssistant,
    login,
    fetchMe,
    logout,
  }
})
