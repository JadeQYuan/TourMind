<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { encryptPassword } from '@/utils/passwordEncrypt'
import logoUrl from '@/assets/logo.svg'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

// ── Login form ────────────────────────────────────────────────────
const form = reactive({ phone: '', password: '', rememberMe: false })
const loading = ref(false)

// ── Change-password step ──────────────────────────────────────────
const showChangePassword = ref(false)
const cpForm = reactive({ oldPassword: '', newPassword: '', confirmPassword: '' })
const cpLoading = ref(false)

async function handleLogin() {
  if (!form.phone || !form.password) {
    message.warning('请输入手机号和密码')
    return
  }
  loading.value = true
  try {
    const encrypted = await encryptPassword(form.password)
    const result = await auth.login(form.phone, encrypted, form.rememberMe)
    if (result?.must_change_password) {
      // Show inline password-change step
      cpForm.oldPassword = encrypted
      showChangePassword.value = true
      return
    }
    const redirect = (route.query.redirect as string) || '/orders'
    router.push(redirect)
  } catch (e: any) {
    message.error(e?.message ?? String(e))
  } finally {
    loading.value = false
  }
}

async function handleChangePassword() {
  if (!cpForm.newPassword || cpForm.newPassword !== cpForm.confirmPassword) {
    message.warning('两次输入的密码不一致')
    return
  }
  cpLoading.value = true
  try {
    const encryptedNew = await encryptPassword(cpForm.newPassword)
    await authApi.changePassword(cpForm.oldPassword, encryptedNew)
    message.success('密码修改成功，请重新登录')
    auth.logout()
    showChangePassword.value = false
    form.password = ''
  } catch (e: any) {
    message.error(e?.message ?? '密码修改失败')
  } finally {
    cpLoading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-header">
      <img :src="logoUrl" alt="智游管家 TourMind" class="login-logo" />
      <p class="login-slogan">专业旅行社智能管理平台</p>
    </div>

    <!-- Password Change (first login) -->
    <a-card v-if="showChangePassword" class="login-card">
      <a-alert
        message="首次登录需要修改密码（≥12位，含大小写、数字、特殊符号）"
        type="warning"
        show-icon
        style="margin-bottom: 16px"
      />
      <a-form layout="vertical">
        <a-form-item label="新密码" required>
          <a-input-password v-model:value="cpForm.newPassword" size="large" placeholder="≥12位，含大小写字母、数字、特殊字符" />
        </a-form-item>
        <a-form-item label="确认新密码" required>
          <a-input-password v-model:value="cpForm.confirmPassword" size="large" />
        </a-form-item>
        <a-button type="primary" block size="large" :loading="cpLoading" @click="handleChangePassword">
          设置新密码
        </a-button>
      </a-form>
    </a-card>

    <!-- Normal Login -->
    <a-card v-else class="login-card">
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
