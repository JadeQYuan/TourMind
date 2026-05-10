<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { useAuthStore } from '@/stores/auth'
import { FilterOutlined } from '@ant-design/icons-vue'
const windowWidth = ref(window.innerWidth)
import { userApi } from '@/api/user'
import type { UserInfo } from '@/types'
import { useBreakpoint } from '@/composables/useBreakpoint'
import { genPassword } from '@/utils/genPassword'
import { encryptPassword } from '@/utils/passwordEncrypt'

const { isMobile } = useBreakpoint()

const users = ref<UserInfo[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, page_size: 20, keyword: undefined as string | undefined, role: undefined as string | undefined, status: 'enabled' as string | undefined })
const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<any>({ role: 'assistant', status: 'enabled' })

const drawerViewOpen = ref(false)
const drawerViewData = ref<UserInfo | null>(null)
const drawerLoading = ref(false)

const ROLES: Record<string, string> = { system_admin: '系统管理员', admin: '管理员', assistant: '助理' }
const ROLE_COLOR: Record<string, string> = { system_admin: 'red', admin: 'blue', assistant: 'green' }
const auth = useAuthStore()

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await userApi.list(query)
  let list = res.data?.items ?? res.data ?? []
  // 前端兜底过滤：管理员不可见系统管理员
  if (auth.user?.role === 'admin') {
    list = list.filter(u => u.role !== 'system_admin')
  }
  users.value = list
  total.value = res.data?.total ?? list.length
  loading.value = false
}

function openCreate() { editingId.value = null; form.value = { role: 'assistant', status: 'enabled' }; modalOpen.value = true }
function openEdit(u: UserInfo) {
  if (u.role === 'system_admin') { message.warning('系统管理员不可编辑'); return }
  editingId.value = u.id; form.value = { ...u, phone: u.phone ?? undefined }; modalOpen.value = true
}

async function save() {
  if (!form.value.name?.trim()) { message.error('请输入姓名'); return }
  if (!form.value.phone?.trim()) { message.error('请输入手机号'); return }
  if (editingId.value) {
    await userApi.update(editingId.value, form.value)
    message.success('保存成功')
  } else {
    const plain = genPassword(12)
    const encrypted = await encryptPassword(plain)
    await userApi.create({ ...form.value, password: encrypted })
    Modal.info({ title: '初始密码', content: `初始密码：${plain}，请记录并告知用户` })
  }
  modalOpen.value = false
  fetchList()
}

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerViewData.value = null
  drawerLoading.value = true
  try {
    const res = await userApi.get(id)
    drawerViewData.value = res.data
  } catch {
    message.error('加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function resetPwd(u: UserInfo) {
  if (u.role === 'system_admin') { message.warning('系统管理员不可重置密码'); return }
  Modal.confirm({
    title: `确认重置 ${u.name} 的密码？`,
    onOk: async () => {
      const plain = genPassword(12)
      const encrypted = await encryptPassword(plain)
      await userApi.resetPassword(u.id, encrypted)
      Modal.info({ title: '新密码', content: `初始密码：${plain}，请告知用户` })
    },
  })
}

async function toggleActive(u: UserInfo) {
  if (u.role === 'system_admin') { message.warning('系统管理员不可操作'); return }
  await userApi.patchStatus(u.id)
  message.success(u.status === 'enabled' ? '已禁用' : '已启用')
  fetchList()
}

const mobileFilterOpen = ref(false)
const mobileFilter = reactive({ keyword: undefined as string | undefined, role: undefined as string | undefined, status: 'enabled' as string | undefined })

const activeFilterCount = computed(() => {
  let n = 0
  if (query.keyword) n++
  if (query.role) n++
  if (query.status !== 'enabled') n++
  return n
})

function openMobileFilter() {
  mobileFilter.keyword = query.keyword
  mobileFilter.role = query.role
  mobileFilter.status = query.status
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  query.keyword = mobileFilter.keyword
  query.role = mobileFilter.role
  query.status = mobileFilter.status
  query.page = 1
  mobileFilterOpen.value = false
  fetchList()
}

function resetMobileFilter() {
  mobileFilter.keyword = undefined
  mobileFilter.role = undefined
  mobileFilter.status = 'enabled'
}

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '姓名', dataIndex: 'name', width: 100 },
  { title: '手机号', dataIndex: 'phone', width: 140 },
  { title: '角色', key: 'role', width: 110 },
  { title: '状态', key: 'status', width: 80, align: 'center' },
  { title: '最后登录', dataIndex: 'last_login', width: 160, customRender: ({ text }: any) => text ? text.slice(0, 16).replace('T', ' ') : '-' },
  { title: '操作', key: 'action', width: 210, fixed: 'right' as const },
]
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="姓名/手机">
          <a-input v-model:value="query.keyword" placeholder="搜索姓名或手机号" allow-clear style="width:170px" @change="() => { query.page = 1; fetchList() }" @pressEnter="() => { query.page = 1; fetchList() }" />
        </a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="query.role" placeholder="全部" allow-clear style="width:120px" @change="() => { query.page = 1; fetchList() }">
            <a-select-option v-if="auth.isSystemAdmin" value="system_admin">系统管理员</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="assistant">助理</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="query.status" placeholder="全部" allow-clear style="width:90px" @change="() => { query.page = 1; fetchList() }">
            <a-select-option value="enabled">启用</a-select-option>
            <a-select-option value="disabled">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="() => { query.keyword = undefined; query.role = undefined; query.status = 'enabled'; query.page = 1; fetchList() }">重置</a-button>
        </a-form-item>
      </a-form>
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter"><template #icon><filter-outlined /></template>筛选</a-button>
      </a-badge>
      <a-button type="primary" @click="openCreate">新增用户</a-button>
    </div>

    <!-- 移动端卡片 -->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="users" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;color:#111827;font-size:14px">{{ record.name }}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">{{ record.phone }}</div>
                    <span style="margin-top:4px;display:inline-block">
                      <a-tag :color="ROLE_COLOR[record.role]" style="margin:0">{{ ROLES[record.role] ?? record.role }}</a-tag>
                    </span>
                  </div>
                  <a-tag :color="record.status === 'enabled' ? 'green' : 'default'" style="margin:0">{{ record.status === 'enabled' ? '启用' : '禁用' }}</a-tag>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:8px;flex-wrap:wrap">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button size="small" :disabled="record.role === 'system_admin'" @click="openEdit(record)">编辑</a-button>
                  <a-button size="small" :disabled="record.role === 'system_admin'" @click="toggleActive(record)">{{ record.status === 'enabled' ? '禁用' : '启用' }}</a-button>
                  <a-button size="small" :disabled="record.role === 'system_admin'" @click="resetPwd(record)">重置密码</a-button>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
        <div style="display:flex;justify-content:center;margin-top:12px">
          <a-pagination :total="total" :current="query.page" :page-size="query.page_size" size="small" :show-size-changer="false"
            @change="(p: number) => { query.page = p; fetchList() }" />
        </div>
      </a-spin>
    </template>

    <!-- 桌面端表格 -->
    <a-table v-else :data-source="users" :columns="columns" :loading="loading"
      :scroll="{ x: 920 }"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchList() } }"
      row-key="id" size="middle">
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ (query.page - 1) * query.page_size + index + 1 }}</template>
        <template v-else-if="column.key === 'role'">
          <a-tag :color="ROLE_COLOR[record.role]">{{ ROLES[record.role] ?? record.role }}</a-tag>
        </template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'enabled' ? 'green' : 'default'">{{ record.status === 'enabled' ? '启用' : '禁用' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button size="small" :disabled="record.role === 'system_admin'" @click="openEdit(record)">编辑</a-button>
            <a-button size="small" :disabled="record.role === 'system_admin'" @click="toggleActive(record)">{{ record.status === 'enabled' ? '禁用' : '启用' }}</a-button>
            <a-button size="small" :disabled="record.role === 'system_admin'" @click="resetPwd(record)">重置密码</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉 -->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="55vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="姓名/手机"><a-input v-model:value="mobileFilter.keyword" placeholder="搜索姓名或手机号" allow-clear /></a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="mobileFilter.role" placeholder="全部" allow-clear style="width:100%">
            <a-select-option v-if="auth.isSystemAdmin" value="system_admin">系统管理员</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="assistant">助理</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="mobileFilter.status" placeholder="全部" allow-clear style="width:100%">
            <a-select-option value="enabled">启用</a-select-option>
            <a-select-option value="disabled">禁用</a-select-option>
          </a-select>
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space style="width:100%;justify-content:flex-end">
          <a-button @click="resetMobileFilter">重置</a-button>
          <a-button type="primary" @click="applyMobileFilter">确认</a-button>
        </a-space>
      </template>
    </a-drawer>

    <!-- 查看抽屉 -->
    <a-drawer
      title="用户详情"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerViewData">
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="姓名">{{ drawerViewData.name }}</a-descriptions-item>
            <a-descriptions-item label="手机号">{{ drawerViewData.phone ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="角色">
              <a-tag :color="ROLE_COLOR[drawerViewData.role]">{{ ROLES[drawerViewData.role] ?? drawerViewData.role }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="drawerViewData.status === 'enabled' ? 'green' : 'default'">{{ drawerViewData.status === 'enabled' ? '启用' : '禁用' }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="最后登录">{{ drawerViewData.last_login ? drawerViewData.last_login.slice(0, 16).replace('T', ' ') : '-' }}</a-descriptions-item>
            <a-descriptions-item label="备注">{{ drawerViewData.remark ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="创建时间">{{ drawerViewData.created_at?.slice(0, 16).replace('T', ' ') }}</a-descriptions-item>
          </a-descriptions>
        </template>
      </a-spin>
    </a-drawer>

    <a-drawer
      :title="editingId ? '编辑用户' : '新增用户'"
      :open="modalOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="modalOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="姓名" required><a-input v-model:value="form.name" placeholder="请输入姓名" /></a-form-item>
        <a-form-item label="手机号" required>
          <a-input v-model:value="form.phone" placeholder="请输入手机号" :disabled="!!editingId" />
        </a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="form.role" style="width:100%">
            <a-select-option v-if="auth.user?.role === 'system_admin'" value="system_admin">系统管理员</a-select-option>
            <a-select-option value="admin">管理员</a-select-option>
            <a-select-option value="assistant">助理</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="form.status" style="width:100%">
            <a-select-option value="enabled">启用</a-select-option>
            <a-select-option value="disabled">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="form.remark" placeholder="请输入备注" :rows="3" allow-clear />
        </a-form-item>
        <a-alert v-if="!editingId" type="info" message="创建后系统自动生成初始密码" show-icon />
      </a-form>
      <template #footer>
        <a-space style="width:100%;justify-content:flex-end">
          <a-button @click="modalOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
