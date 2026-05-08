<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { authApi } from '@/api/auth'
import { encryptPassword } from '@/utils/passwordEncrypt'
import { message } from 'ant-design-vue'
import logoIconUrl from '@/assets/logo-icon.svg'
import { Grid } from 'ant-design-vue'
import {
  DashboardOutlined, FileTextOutlined, ContainerOutlined,
  AccountBookOutlined, ShopOutlined, BankOutlined, TeamOutlined,
  UserOutlined, MenuOutlined, AppstoreOutlined, ProfileOutlined,
  AuditOutlined, SafetyOutlined,
} from '@ant-design/icons-vue'

const auth = useAuthStore()
const router = useRouter()
const screens = Grid.useBreakpoint()
const mobileMenuOpen = ref(false)
const role = computed(() => auth.user?.role)

// md ≥ 768px → show inline sider; lg ≥ 992px → sider expanded
const showInlineSider = computed(() => !!screens.value?.md)
const siderCollapsed = computed(() => !screens.value?.lg)

const selectedKeys = computed(() => [useRouter().currentRoute.value.path])

function handleMenuClick({ key }: { key: string }) {
  mobileMenuOpen.value = false
  router.push(key)
}

function logout() {
  auth.logout()
  router.push('/login')
}

const pwdModalOpen = ref(false)
const pwdLoading = ref(false)
const pwdForm = reactive({ old: '', new_: '', confirm: '' })

function resetPwdForm() {
  pwdForm.old = ''
  pwdForm.new_ = ''
  pwdForm.confirm = ''
}

const ROLE_AVATAR_COLOR: Record<string, string> = {
  system_admin: '#ef4444',
  admin: '#10b981',
  assistant: '#3b82f6',
}

async function changePassword() {
  if (!pwdForm.old) { message.error('请输入当前密码'); return }
  if (pwdForm.new_.length < 1) { message.error('请输入新密码'); return }
  if (pwdForm.new_ !== pwdForm.confirm) { message.error('两次密码不一致'); return }
  pwdLoading.value = true
  try {
    const encryptedOld = await encryptPassword(pwdForm.old)
    const encryptedNew = await encryptPassword(pwdForm.new_)
    await authApi.changePassword(encryptedOld, encryptedNew)
    message.success('密码修改成功，请重新登录')
    pwdModalOpen.value = false
    setTimeout(() => { auth.logout(); router.push('/login') }, 1500)
  } catch (err: any) {
    message.error(err ?? '修改失败')
  } finally {
    pwdLoading.value = false
  }
}
</script>

<template>
  <a-layout style="height: 100vh; overflow: hidden; background: linear-gradient(135deg, #f0fdf9 0%, #e0f2fe 50%, #f0fdf4 100%)">
    <!-- 平板/桌面端内联侧边栏 -->
    <a-layout-sider
      v-if="showInlineSider"
      theme="light"
      :width="216"
      :collapsed="siderCollapsed"
      :collapsed-width="64"
      :trigger="null"
      style="background:transparent"
    >
      <div class="sider-glass" :class="{ 'sider-glass-collapsed': siderCollapsed }">
        <div class="logo" :class="{ 'logo-collapsed': siderCollapsed }">
        <img :src="logoIconUrl" alt="" class="logo-icon" />
        <span v-show="!siderCollapsed" class="logo-text">智游管家</span>
      </div>
      <a-menu
        theme="light"
        mode="inline"
        :selected-keys="[$route.path]"
        :inline-collapsed="siderCollapsed"
        style="background:transparent;border:none"
        @click="handleMenuClick"
      >
        <a-menu-item v-if="role !== 'assistant'" key="/dashboard"><dashboard-outlined /><span>数据看板</span></a-menu-item>
        <a-menu-item-group :title="siderCollapsed ? '' : '业务管理'">
          <a-menu-item key="/orders"><profile-outlined /><span>订单管理</span></a-menu-item>
          <a-menu-item key="/itineraries"><file-text-outlined /><span>行程管理</span></a-menu-item>
          <a-menu-item key="/contracts"><container-outlined /><span>合同管理</span></a-menu-item>
          <a-menu-item key="/bills"><account-book-outlined /><span>账单管理</span></a-menu-item>
        </a-menu-item-group>
        <a-menu-item-group :title="siderCollapsed ? '' : '基础配置'">
          <a-menu-item key="/products"><appstore-outlined /><span>产品管理</span></a-menu-item>
          <a-menu-item key="/suppliers"><shop-outlined /><span>供应商</span></a-menu-item>
          <a-menu-item v-if="role !== 'assistant'" key="/accounts"><bank-outlined /><span>账户管理</span></a-menu-item>
          <a-menu-item v-if="role !== 'assistant'" key="/users"><team-outlined /><span>用户管理</span></a-menu-item>
        </a-menu-item-group>
        <a-menu-item-group v-if="role === 'system_admin'" :title="siderCollapsed ? '' : '运维审计'">
          <a-menu-item key="/audit-logs"><audit-outlined /><span>审计日志</span></a-menu-item>
        </a-menu-item-group>
      </a-menu>
      </div>
    </a-layout-sider>

    <a-layout style="background:transparent; display:flex; flex-direction:column; overflow:hidden">
      <a-layout-header class="app-header">
        <!-- 手机端汉堡菜单按钮 -->
        <a-button
          v-if="!showInlineSider"
          type="text"
          class="hamburger-btn"
          @click="mobileMenuOpen = true"
        >
          <menu-outlined />
        </a-button>
        <div style="flex:1" />
        <a-space>
          <a-popover trigger="hover" placement="bottomRight">
            <template #content>
              <div style="min-width:200px">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px">
                  <a-avatar :style="{ background: ROLE_AVATAR_COLOR[auth.user?.role ?? ''] ?? '#0d9488' }" :size="40">
                    {{ auth.user?.full_name?.slice(0,1) }}
                  </a-avatar>
                  <div>
                    <div style="font-weight:600;color:#111827">{{ auth.user?.full_name }}</div>
                    <div style="font-size:12px;color:#6b7280">{{ auth.user?.employee_id }}</div>
                  </div>
                </div>
                <a-divider style="margin:8px 0" />
                <div style="display:flex;flex-direction:column;gap:4px;font-size:13px;color:#374151">
                  <div v-if="auth.user?.phone"><span style="color:#9ca3af;margin-right:8px">手机号</span>{{ auth.user.phone }}</div>
                  <div v-if="auth.user?.employee_id"><span style="color:#9ca3af;margin-right:8px">工号</span>{{ auth.user.employee_id }}</div>
                  <div><span style="color:#9ca3af;margin-right:8px">角色</span>
                    <a-tag :color="{ system_admin: 'red', admin: 'green', assistant: 'blue' }[auth.user?.role ?? ''] ?? 'default'" style="margin:0">
                      {{ { system_admin: '系统管理员', admin: '管理员', assistant: '助理' }[auth.user?.role ?? ''] }}
                    </a-tag>
                  </div>
                </div>
                <a-divider style="margin:8px 0" />
                <a-button type="link" size="small" style="padding:0;color:#0d9488" @click="pwdModalOpen = true">修改密码</a-button>
              </div>
            </template>
            <span class="header-username">
              <a-avatar :size="28" :style="{ background: ROLE_AVATAR_COLOR[auth.user?.role ?? ''] ?? '#0d9488', fontSize: '12px', marginRight: '6px' }">{{ auth.user?.full_name?.slice(0,1) }}</a-avatar>
              {{ auth.user?.full_name }}
            </span>
          </a-popover>
          <a-button type="link" style="color:#0d9488" @click="logout">退出</a-button>
        </a-space>
      </a-layout-header>
      <a-layout-content :style="{ margin: screens?.md ? '20px 24px 24px' : '12px 8px 16px', padding: 0, overflowY: 'auto', flex: 1 }">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>

  <!-- 修改密码 Modal -->
  <a-modal
    title="修改密码"
    :open="pwdModalOpen"
    :confirm-loading="pwdLoading"
    ok-text="确认修改"
    cancel-text="取消"
    @ok="changePassword"
    @cancel="pwdModalOpen = false"
    @after-close="resetPwdForm"
  >
    <a-form layout="vertical" style="margin-top:8px">
      <a-form-item label="当前密码">
        <a-input-password v-model:value="pwdForm.old" placeholder="请输入当前密码" />
      </a-form-item>
      <a-form-item label="新密码">
        <a-input-password v-model:value="pwdForm.new_" placeholder="至少8位，含大写、小写、数字" />
      </a-form-item>
      <a-form-item label="确认新密码">
        <a-input-password v-model:value="pwdForm.confirm" placeholder="再次输入新密码" />
      </a-form-item>
    </a-form>
  </a-modal>

  <!-- 手机端抽屉导航 -->
  <a-drawer
    v-if="!showInlineSider"
    placement="left"
    :open="mobileMenuOpen"
    :width="216"
    :body-style="{ padding: 0, background: 'transparent' }"
    :drawer-style="{ background: 'rgba(240,253,249,0.55)', backdropFilter: 'blur(16px)', WebkitBackdropFilter: 'blur(16px)', borderRight: '1px solid rgba(255,255,255,0.5)' }"
    :header-style="{ display: 'none' }"
    @close="mobileMenuOpen = false"
  >
    <div class="logo">
      <img :src="logoIconUrl" alt="" class="logo-icon" />
      <span class="logo-text">智游管家</span>
    </div>
    <a-menu
      theme="light"
      mode="inline"
      :selected-keys="[$route.path]"
      style="background:transparent;border:none"
      @click="handleMenuClick"
    >
      <a-menu-item v-if="role !== 'assistant'" key="/dashboard"><dashboard-outlined /><span>数据看板</span></a-menu-item>
      <a-menu-item-group title="业务管理">
        <a-menu-item key="/orders"><profile-outlined /><span>订单管理</span></a-menu-item>
        <a-menu-item key="/itineraries"><file-text-outlined /><span>行程管理</span></a-menu-item>
        <a-menu-item key="/contracts"><container-outlined /><span>合同管理</span></a-menu-item>
        <a-menu-item key="/bills"><account-book-outlined /><span>账单管理</span></a-menu-item>
      </a-menu-item-group>
      <a-menu-item-group title="基础配置">
        <a-menu-item key="/products"><appstore-outlined /><span>产品管理</span></a-menu-item>
        <a-menu-item key="/suppliers"><shop-outlined /><span>供应商</span></a-menu-item>
        <a-menu-item v-if="role !== 'assistant'" key="/accounts"><bank-outlined /><span>账户管理</span></a-menu-item>
        <a-menu-item v-if="role !== 'assistant'" key="/users"><team-outlined /><span>用户管理</span></a-menu-item>
      </a-menu-item-group>
      <a-menu-item-group v-if="role === 'system_admin'" title="运维审计">
        <a-menu-item key="/audit-logs"><audit-outlined /><span>审计日志</span></a-menu-item>
      </a-menu-item-group>
    </a-menu>
  </a-drawer>
</template>

<style scoped>
.sider-glass {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  background: rgba(240, 253, 249, 0.55);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-right: 1px solid rgba(255, 255, 255, 0.5);
  box-shadow: 2px 0 12px rgba(13, 148, 136, 0.06);
  transition: width 0.2s;
}
.sider-glass-collapsed {
  width: 64px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 20px 20px 16px;
}
.logo-collapsed {
  padding: 20px 0 16px;
  justify-content: center;
}
.logo-icon {
  height: 34px;
  width: 34px;
  flex-shrink: 0;
  border-radius: 8px;
}
.logo-text {
  color: #0d9488;
  font-size: 16px;
  font-weight: 700;
  font-family: 'PingFang SC','Microsoft YaHei',system-ui,sans-serif;
  white-space: nowrap;
}
.app-header {
  background: transparent;
  padding: 0 24px 0 16px;
  display: flex;
  align-items: center;
  box-shadow: none;
  border-bottom: none;
}
.hamburger-btn {
  font-size: 18px;
  color: #374151;
  margin-right: 4px;
}
.header-username {
  color: #374151;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
  transition: background 0.2s;
}
.header-username:hover {
  background: #e6f4f1;
  color: #0d9488;
}
</style>
