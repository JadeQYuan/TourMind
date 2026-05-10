<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { FilterOutlined } from '@ant-design/icons-vue'
const windowWidth = ref(window.innerWidth)
import { accountApi } from '@/api/account'
import { userApi } from '@/api/user'
import type { Account } from '@/types'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const accounts = ref<Account[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, page_size: 20, keyword: undefined as string | undefined, type: undefined as string | undefined, status: 'enabled' as string | undefined })
const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<Account>>({ type: 'bank', status: 'enabled' })

const drawerViewOpen = ref(false)
const drawerViewData = ref<Account | null>(null)
const drawerLoading = ref(false)

const userOptions = ref<{ id: number; name: string }[]>([])

const TYPES: Record<string, string> = {
  bank: '银行卡', wechat: '微信', alipay: '支付宝', cash: '现金', pos: 'POS机', other: '其他',
}

onMounted(async () => {
  await Promise.all([fetchList(), loadUsers()])
})

async function loadUsers() {
  const res = await userApi.list({ page: 1, page_size: 100 })
  userOptions.value = (res.data?.items ?? res.data ?? []).map((u: any) => ({ id: u.id, name: u.full_name ?? u.name }))
}

async function fetchList() {
  loading.value = true
  const res = await accountApi.list(query)
  accounts.value = res.data?.items ?? res.data ?? []
  total.value = res.data?.total ?? accounts.value.length
  loading.value = false
}

function openCreate() { editingId.value = null; form.value = { type: 'bank', status: 'enabled' }; modalOpen.value = true }
function openEdit(a: Account) { editingId.value = a.id; form.value = { ...a, user_id: (a as any).user_id ?? undefined, user_name: (a as any).user_name ?? undefined }; modalOpen.value = true }

function onUserChange(userId: number) {
  const u = userOptions.value.find(x => x.id === userId)
  if (u) form.value.user_name = u.name
}

async function save() {
  if (!form.value.name?.trim()) { message.error('请输入账户名称'); return }
  if (editingId.value) {
    await accountApi.update(editingId.value, form.value)
  } else {
    await accountApi.create(form.value as any)
  }
  modalOpen.value = false
  message.success('保存成功')
  fetchList()
}

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerViewData.value = null
  drawerLoading.value = true
  try {
    const res = await accountApi.get(id)
    drawerViewData.value = res.data
  } catch {
    message.error('加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function toggleActive(record: Account) {
  const newStatus = record.status === 'enabled' ? 'disabled' : 'enabled'
  await accountApi.update(record.id, { status: newStatus })
  message.success(newStatus === 'enabled' ? '已启用' : '已停用')
  fetchList()
}

const mobileFilterOpen = ref(false)
const mobileFilter = reactive({ keyword: undefined as string | undefined, type: undefined as string | undefined, status: 'enabled' as string | undefined })

const activeFilterCount = computed(() => {
  let n = 0
  if (query.keyword) n++
  if (query.type) n++
  if (query.status !== 'enabled') n++
  return n
})

function openMobileFilter() {
  mobileFilter.keyword = query.keyword
  mobileFilter.type = query.type
  mobileFilter.status = query.status
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  query.keyword = mobileFilter.keyword
  query.type = mobileFilter.type
  query.status = mobileFilter.status
  query.page = 1
  mobileFilterOpen.value = false
  fetchList()
}

function resetMobileFilter() {
  mobileFilter.keyword = undefined
  mobileFilter.type = undefined
  mobileFilter.status = 'enabled'
}

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '账户名称', dataIndex: 'name', width: 180, ellipsis: true },
  { title: '类型', dataIndex: 'type', width: 90, customRender: ({ text }: any) => TYPES[text] ?? text },
  { title: '负责人', dataIndex: 'user_name', width: 100 },
  { title: '状态', key: 'status', width: 80, align: 'center' },
  { title: '操作', key: 'action', width: 160, fixed: 'right' as const },
]
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="账户名称">
          <a-input v-model:value="query.keyword" placeholder="搜索账户名称" allow-clear style="width:160px" @change="() => { query.page = 1; fetchList() }" @pressEnter="() => { query.page = 1; fetchList() }" />
        </a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="query.type" placeholder="全部" allow-clear style="width:110px" @change="() => { query.page = 1; fetchList() }">
            <a-select-option v-for="(label, key) in TYPES" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="query.status" placeholder="全部" allow-clear style="width:90px" @change="() => { query.page = 1; fetchList() }">
            <a-select-option value="enabled">启用</a-select-option>
            <a-select-option value="disabled">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="() => { query.keyword = undefined; query.type = undefined; query.status = 'enabled'; query.page = 1; fetchList() }">重置</a-button>
        </a-form-item>
      </a-form>
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter"><template #icon><filter-outlined /></template>筛选</a-button>
      </a-badge>
      <a-button type="primary" @click="openCreate">新增账户</a-button>
    </div>

    <!-- 移动端卡片 -->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="accounts" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;color:#111827;font-size:14px">{{ record.name }}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">类型：{{ TYPES[record.type] ?? record.type }}</div>
                    <div v-if="record.user_name" style="font-size:12px;color:#9ca3af;margin-top:2px">负责人：{{ record.user_name }}</div>
                  </div>
                  <a-tag :color="record.status === 'enabled' ? 'green' : 'default'" style="margin:0">{{ record.status === 'enabled' ? '启用' : '停用' }}</a-tag>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:8px">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button size="small" @click="openEdit(record)">编辑</a-button>
                  <a-button size="small" @click="toggleActive(record)">{{ record.status === 'enabled' ? '停用' : '启用' }}</a-button>
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
    <a-table v-else :data-source="accounts" :columns="columns" :loading="loading"
      :scroll="{ x: 840 }"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchList() } }"
      row-key="id" size="middle">
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ (query.page - 1) * query.page_size + index + 1 }}</template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="record.status === 'enabled' ? 'green' : 'default'">{{ record.status === 'enabled' ? '启用' : '停用' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
            <a-button size="small" @click="toggleActive(record)">{{ record.status === 'enabled' ? '停用' : '启用' }}</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉 -->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="55vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="账户名称"><a-input v-model:value="mobileFilter.keyword" placeholder="搜索账户名称" allow-clear /></a-form-item>
        <a-form-item label="类型">
          <a-select v-model:value="mobileFilter.type" placeholder="全部" allow-clear style="width:100%">
            <a-select-option v-for="(label, key) in TYPES" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="mobileFilter.status" placeholder="全部" allow-clear style="width:100%">
            <a-select-option value="enabled">启用</a-select-option>
            <a-select-option value="disabled">停用</a-select-option>
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
      title="账户详情"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerViewData">
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="账户名称">{{ drawerViewData.name }}</a-descriptions-item>
            <a-descriptions-item label="账户类型">{{ TYPES[drawerViewData.type] ?? drawerViewData.type }}</a-descriptions-item>
            <a-descriptions-item label="负责人">{{ drawerViewData.user_name ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="备注">
              <span style="white-space:pre-wrap">{{ drawerViewData.remark ?? '-' }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="drawerViewData.status === 'enabled' ? 'green' : 'default'">{{ drawerViewData.status === 'enabled' ? '启用' : '停用' }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="创建时间">{{ drawerViewData.created_at?.slice(0, 16).replace('T', ' ') }}</a-descriptions-item>
          </a-descriptions>
        </template>
      </a-spin>
    </a-drawer>

    <a-drawer
      :title="editingId ? '编辑账户' : '新增账户'"
      :open="modalOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="modalOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="账户名称" required><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="账户类型">
          <a-select v-model:value="form.type" style="width:100%">
            <a-select-option v-for="(label, key) in TYPES" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="负责人">
          <a-select v-model:value="form.user_id" placeholder="请选择负责人" allow-clear style="width:100%" @change="onUserChange">
            <a-select-option v-for="u in userOptions" :key="u.id" :value="u.id">{{ u.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注"><a-textarea v-model:value="form.remark" :rows="2" /></a-form-item>
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
