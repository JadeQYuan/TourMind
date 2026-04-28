<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { FilterOutlined } from '@ant-design/icons-vue'
import { contractApi } from '@/api/contract'
import type { ContractListItem, Contract } from '@/types'
import ContractCreateForm from './ContractFormView.vue'

import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const router = useRouter()
const items = ref<ContractListItem[]>([])
const loading = ref(false)
const filterStatus = ref<string | undefined>()
const filterCustomer = ref('')

const drawerOpen = ref(false)
// const contractFormRef = ref<InstanceType<typeof ContractCreateForm>>() // 未使用，移除
const windowWidth = ref(window.innerWidth)

const drawerViewOpen = ref(false)
const drawerViewData = ref<Contract | null>(null)
const drawerLoading = ref(false)

const mobileFilterOpen = ref(false)
const mobileFilter = { status: ref<string | undefined>(undefined), customer: ref('') }

const activeFilterCount = computed(() => {
  let n = 0
  if (filterStatus.value) n++
  if (filterCustomer.value) n++
  return n
})

function openMobileFilter() {
  mobileFilter.status.value = filterStatus.value
  mobileFilter.customer.value = filterCustomer.value
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  filterStatus.value = mobileFilter.status.value
  filterCustomer.value = mobileFilter.customer.value
  mobileFilterOpen.value = false
  load()
}

function resetMobileFilter() {
  mobileFilter.status.value = undefined
  mobileFilter.customer.value = ''
}

const STATUS_COLOR: Record<string, string> = {
  pending_sign: 'orange',
  signed: 'success',
  in_progress: 'processing',
  completed: 'default',
  cancelled: 'error',
}
const STATUS_LABEL: Record<string, string> = {
  pending_sign: '待签署',
  signed: '已签署',
  in_progress: '进行中',
  completed: '已完成',
  cancelled: '已取消',
}

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '合同编号', dataIndex: 'contract_no', width: 180 },
  { title: '客户', dataIndex: 'customer_name', width: 100 },
  { title: '状态', key: 'status', width: 100 },
  { title: '签署时间', key: 'signed_at', width: 160 },
  { title: '创建时间', dataIndex: 'created_at', width: 160, customRender: ({ text }: any) => text?.slice(0, 16).replace('T', ' ') },
  { title: '操作', key: 'action', width: 200, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const res = await contractApi.list({ status: filterStatus.value, customer_name: filterCustomer.value || undefined })
    if (Array.isArray(res.data)) {
      items.value = res.data
    } else if (res.data && Array.isArray(res.data.items)) {
      items.value = res.data.items
    } else {
      items.value = []
    }
  } finally {
    loading.value = false
  }
}

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerViewData.value = null
  drawerLoading.value = true
  try {
    const res = await contractApi.get(id)
    drawerViewData.value = res.data
  } catch {
    message.error('加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function doShare(record: ContractListItem) {
  const url = `${location.origin}/sign/${record.share_token}`
  try {
    await navigator.clipboard.writeText(url)
    message.success('签署链接已复制')
  } catch {
    Modal.info({ title: '签署链接', content: url, okText: '关闭' })
  }
}

// async function revokeShare(record: ContractListItem) {
//   try {
//     await contractApi.revokeShare(record.id)
//     message.success('分享链接已撤销')
//     load()
//   } catch {
//     message.error('撤销失败')
//   }
// }
// 编辑抽屉相关
const editDrawerOpen = ref(false)
const editId = ref<number | null>(null)
const contractEditForm = ref<InstanceType<typeof ContractCreateForm> | null>(null)
function openEditDrawer(id: number) {
  editId.value = id
  editDrawerOpen.value = true
}

onMounted(load)
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="状态">
          <a-select v-model:value="filterStatus" placeholder="全部" allow-clear style="width:120px" @change="load">
            <a-select-option v-for="(label, key) in STATUS_LABEL" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="客户">
          <a-input v-model:value="filterCustomer" placeholder="客户姓名" allow-clear @change="load" @press-enter="load" />
        </a-form-item>
        <a-form-item>
          <a-button @click="() => { filterStatus = undefined; filterCustomer = ''; load() }">重置</a-button>
        </a-form-item>
      </a-form>
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter"><template #icon><filter-outlined /></template>筛选</a-button>
      </a-badge>
      <a-button type="primary" @click="drawerOpen = true">新建合同</a-button>
    </div>

    <!-- 移动端卡片 -->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="items" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;color:#111827;font-size:14px">{{ record.contract_no }}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">客户：{{ record.customer_name }}</div>
                    <div v-if="record.signed_at" style="font-size:12px;color:#9ca3af;margin-top:2px">签署：{{ record.signed_at.slice(0, 10) }}</div>
                  </div>
                  <a-tag :color="STATUS_COLOR[record.status] ?? 'default'" style="margin:0">{{ STATUS_LABEL[record.status] ?? record.status }}</a-tag>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:8px">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button v-if="record.status === 'pending_sign'" size="small" @click="doShare(record)">分享</a-button>
                  <a-button v-if="record.status === 'pending_sign'" size="small" @click="openEditDrawer(record.id)">编辑</a-button>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
      </a-spin>
    </template>

    <!-- 桌面端表格 -->
    <a-table v-else :columns="columns" :data-source="items" :loading="loading" row-key="id" size="middle" :scroll="{ x: 960 }">
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ index + 1 }}</template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="STATUS_COLOR[record.status] ?? 'default'">{{ STATUS_LABEL[record.status] ?? record.status }}</a-tag>
        </template>
        <template v-else-if="column.key === 'signed_at'">
          {{ record.signed_at ? record.signed_at.slice(0, 16).replace('T', ' ') : '—' }}
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button v-if="record.status === 'pending_sign'" size="small" @click="doShare(record)">分享</a-button>
            <a-button v-if="record.status === 'pending_sign'" size="small" @click="openEditDrawer(record.id)">编辑</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉 -->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="45vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="状态">
          <a-select v-model:value="mobileFilter.status.value" placeholder="全部" allow-clear style="width:100%">
            <a-select-option v-for="(label, key) in STATUS_LABEL" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="客户">
          <a-input v-model:value="mobileFilter.customer.value" placeholder="客户姓名" allow-clear />
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
      title="合同详情"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : Math.min(520, windowWidth)"
      placement="right"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerViewData">
          <a-descriptions :column="isMobile ? 1 : 2" bordered size="small" style="word-break:break-all">
            <a-descriptions-item label="合同编号">{{ drawerViewData.contract_no }}</a-descriptions-item>
            <a-descriptions-item label="甲方">{{ drawerViewData.party_a || drawerViewData.customer_name }}</a-descriptions-item>
            <a-descriptions-item label="甲方联系电话">{{ drawerViewData.party_a_phone || drawerViewData.customer_phone }}</a-descriptions-item>
            <a-descriptions-item label="乙方">{{ drawerViewData.party_b }}</a-descriptions-item>
            <a-descriptions-item label="乙方联系电话">{{ drawerViewData.party_b_phone }}</a-descriptions-item>
            <a-descriptions-item label="客户姓名">{{ drawerViewData.customer_name }}</a-descriptions-item>
            <a-descriptions-item label="手机号">{{ drawerViewData.customer_phone }}</a-descriptions-item>
            <a-descriptions-item label="关联订单">{{ drawerViewData.order_no }}</a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="STATUS_COLOR[drawerViewData.status] ?? 'default'">{{ STATUS_LABEL[drawerViewData.status] ?? drawerViewData.status }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="签署时间">{{ drawerViewData.signed_at ? drawerViewData.signed_at.slice(0, 16).replace('T', ' ') : '-' }}</a-descriptions-item>
            <a-descriptions-item label="创建时间">{{ drawerViewData.created_at?.slice(0, 16).replace('T', ' ') }}</a-descriptions-item>
            <a-descriptions-item label="包含项目">{{ drawerViewData.includes }}</a-descriptions-item>
            <a-descriptions-item label="不含项目">{{ drawerViewData.excludes }}</a-descriptions-item>
            <a-descriptions-item label="退改规则">{{ drawerViewData.cancellation_policy }}</a-descriptions-item>
            <a-descriptions-item v-if="drawerViewData.travel_notice" label="出行提示">{{ drawerViewData.travel_notice }}</a-descriptions-item>
            <a-descriptions-item v-if="drawerViewData.notes" label="备注">{{ drawerViewData.notes }}</a-descriptions-item>
          </a-descriptions>
        </template>
      </a-spin>
    </a-drawer>

    <!-- 新建合同抽屉 -->
    <a-drawer
      title="新建合同"
      :open="drawerOpen"
      :width="isMobile ? '100%' : Math.min(520, windowWidth)"
      placement="right"
      :destroy-on-close="true"
      @close="drawerOpen = false"
    >
      <ContractCreateForm @saved="(id) => { drawerOpen = false; router.push(`/contracts/${id}`) }" @cancel="drawerOpen = false" />
    </a-drawer>

    <!-- 编辑合同抽屉 -->
    <a-drawer
      title="编辑合同"
      :open="editDrawerOpen"
      :width="isMobile ? '100%' : Math.min(520, windowWidth)"
      placement="right"
      :destroy-on-close="true"
      @close="editDrawerOpen = false"
    >
      <template #footer>
        <a-space style="width:100%;justify-content:flex-end">
          <a-button @click="editDrawerOpen = false">取消</a-button>
          <a-button type="primary" :loading="loading" @click="contractEditForm?.save()">保存</a-button>
        </a-space>
      </template>
      <ContractCreateForm
        ref="contractEditForm"
        :editId="editId"
        :showFooter="false"
        @saved="() => { editDrawerOpen = false; load() }"
        @cancel="editDrawerOpen = false"
      />
    </a-drawer>
  </div>
</template>
