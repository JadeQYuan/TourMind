<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { encryptPassword } from '@/utils/passwordEncrypt'
import logoUrl from '@/assets/logo.svg'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// ── Login form ────────────────────────────────────────────────────
const form = reactive({ phone: '', password: '', rememberMe: false })
const loading = ref(false)

async function handleLogin() {
  if (!form.phone || !form.password) {
    message.warning('请输入手机号和密码')
    return
  }
  loading.value = true
  try {
    const encrypted = await encryptPassword(form.password)
    await auth.login(form.phone, encrypted, form.rememberMe)
    const redirect = (route.query.redirect as string) || '/orders'
    router.push(redirect)
  } catch (e: any) {
    message.error(e?.message ?? String(e))
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-header">
      <img :src="logoUrl" alt="智游管家 TourMind" class="login-logo" />
      <p class="login-slogan">专业旅行社智能管理平台</p>
    </div>

    <!-- Normal Login -->
    <a-card class="login-card">
      <a-form :model="form" layout="vertical">
        <a-form-item label="手机号" required>
          <a-input v-model:value="form.phone" placeholder="手机号" size="large" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="form.password" size="large" @keyup.enter="handleLogin" />
        </a-form-item>
        <a-form-item>
          <a-checkbox v-model:checked="form.rememberMe">记住我（7天）</a-checkbox>
        </a-form-item>
        <a-button type="primary" block size="large" :loading="loading" @click="handleLogin">
          登录
        </a-button>
      </a-form>
    </a-card>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f0fdf9 0%, #e0f2fe 50%, #f0fdf4 100%);
}
.login-header {
  text-align: center;
  margin-bottom: 24px;
}
.login-logo {
  height: 52px;
  width: auto;
}
.login-slogan {
  margin-top: 8px;
  color: #64748b;
  font-size: 14px;
}
.login-card {
  width: min(420px, calc(100vw - 32px));
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}
</style>
