<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import { FilterOutlined } from '@ant-design/icons-vue'
import { itineraryApi } from '@/api/itinerary'
import type { ItineraryListItem, Itinerary } from '@/types'
import ItineraryFormView from './ItineraryFormView.vue'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const router = useRouter()
const items = ref<ItineraryListItem[]>([])
const loading = ref(false)
const drawerWidth = Math.min(780, window.innerWidth)
const filterStatus = ref<string | undefined>()
const filterCustomer = ref('')

const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const itineraryFormRef = ref<InstanceType<typeof ItineraryFormView>>()

const drawerViewOpen = ref(false)
const drawerItinerary = ref<Itinerary | null>(null)
const drawerLoading = ref(false)
const drawerCollapseKeys = computed(() =>
  drawerItinerary.value?.days_detail?.map(d => d.seq) ?? []
)

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

function openCreate() { editingId.value = null; drawerOpen.value = true }
function openEdit(id: number) { editingId.value = id; drawerOpen.value = true }
function onSaved(id: number) {
  drawerOpen.value = false
  load()
  // 新建成功后跳转详情
  if (!editingId.value) router.push(`/itineraries/${id}`)
}

const statusOptions = [
  { label: '未开始', value: 'not_started' },
  { label: '行程中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
  { label: '已撤销', value: 'cancelled' },
]

const statusColor: Record<string, string> = {
  not_started: 'default', in_progress: 'processing', completed: 'success', cancelled: 'error',
}
const statusLabel: Record<string, string> = {
  not_started: '未开始', in_progress: '行程中', completed: '已完成', cancelled: '已撤销',
}

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '关联订单', dataIndex: 'order_no', key: 'order_no', width: 180 },
  { title: '客户', dataIndex: 'customer_name', key: 'customer_name', width: 90 },
  { title: '目的地', dataIndex: 'destination', key: 'destination', width: 110 },
  { title: '出发日期', dataIndex: 'start_date', key: 'start_date', width: 110 },
  { title: '结束日期', dataIndex: 'end_date', key: 'end_date', width: 110 },
  { title: '人数', dataIndex: 'pax', key: 'pax', width: 60, align: 'center' as const },
  { title: '状态', dataIndex: 'status', key: 'status', width: 90 },
  { title: '操作', key: 'action', width: 200, fixed: 'right' as const },
]

async function load() {
  loading.value = true
  try {
    const res = await itineraryApi.list({
      status: filterStatus.value,
      keyword: filterCustomer.value || undefined,
    })
    items.value = res.data?.items ?? res.data ?? []
  } finally {
    loading.value = false
  }
}

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerItinerary.value = null
  drawerLoading.value = true
  try {
    const res = await itineraryApi.get(id)
    drawerItinerary.value = res.data
  } catch {
    message.error('行程加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function doMarkComplete(record: ItineraryListItem) {
  await itineraryApi.patchStatus(record.id, 'completed')
  message.success('已标记完成')
  load()
}

function doCancelItinerary(record: ItineraryListItem) {
  Modal.confirm({
    title: '撤销行程',
    content: '确认撤销该行程？撤销后状态不可恢复，行程将标记为"已撤销"。',
    okText: '确认撤销',
    okType: 'danger',
    cancelText: '取消',
    onOk: async () => {
      await itineraryApi.patchStatus(record.id, 'cancelled')
      message.success('行程已撤销')
      load()
    },
  })
}

async function doShare(record: ItineraryListItem) {
  if (!record.share_token) {
    return
  }
  const url = `${location.origin}/public/itinerary/${record.share_token}`
  try {
    await navigator.clipboard.writeText(url)
    message.success('分享链接已复制')
  } catch {
    Modal.info({ title: '分享链接', content: url, okText: '关闭' })
  }
}

onMounted(load)
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="状态">
          <a-select v-model:value="filterStatus" placeholder="全部" allow-clear style="width:120px" :options="statusOptions" @change="load" />
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
      <a-button type="primary" @click="openCreate">新建行程</a-button>
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
                    <div style="font-weight:600;color:#111827;font-size:14px">{{ record.customer_name }} · {{ record.destination }}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">关联订单：{{ record.order_no }}</div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:2px">出发：{{ record.start_date }} — {{ record.end_date }}</div>
                  </div>
                  <!-- 状态标签已移除，按任务要求不再显示在目的地后 -->
                </div>
                <div style="display:flex;justify-content:flex-end;gap:8px;margin-top:8px;flex-wrap:wrap">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button v-if="record.status !== 'cancelled'" size="small" @click="openEdit(record.id)">编辑</a-button>
                  <a-button v-if="record.status === 'in_progress' && dayjs().isAfter(dayjs(record.end_date), 'day')" size="small" @click="doMarkComplete(record)">标记完成</a-button>
                  <a-button v-if="['not_started','in_progress'].includes(record.status) && !dayjs().isAfter(dayjs(record.end_date), 'day')" size="small" danger @click="doCancelItinerary(record)">撤销</a-button>
                  <a-button v-if="['not_started','in_progress'].includes(record.status)" size="small" @click="doShare(record)">分享</a-button>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
      </a-spin>
    </template>

    <!-- 桌面端表格 -->
    <a-table v-else :columns="columns" :data-source="items" :loading="loading" row-key="id" size="middle" :scroll="{ x: 1020 }">
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ index + 1 }}</template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="statusColor[record.status] ?? 'default'">{{ statusLabel[record.status] ?? record.status }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button v-if="record.status !== 'cancelled'" size="small" @click="openEdit(record.id)">编辑</a-button>
            <a-button v-if="record.status === 'in_progress' && dayjs().isAfter(dayjs(record.end_date), 'day')" size="small" @click="doMarkComplete(record)">标记完成</a-button>
            <a-button v-if="['not_started','in_progress'].includes(record.status) && !dayjs().isAfter(dayjs(record.end_date), 'day')" size="small" danger @click="doCancelItinerary(record)">撤销</a-button>
            <a-button v-if="['not_started','in_progress'].includes(record.status)" size="small" @click="doShare(record)">分享</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉 -->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="45vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="状态">
          <a-select v-model:value="mobileFilter.status.value" placeholder="全部" allow-clear style="width:100%" :options="statusOptions" />
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

    <!-- 查看行程抽屉 -->
    <a-drawer
      :title="drawerItinerary ? `${drawerItinerary.customer_name} · ${drawerItinerary.destination}` : '行程详情'"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : drawerWidth"
      placement="right"
      :destroy-on-close="true"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerItinerary">
          <a-descriptions :column="{ xs: 1, sm: 2 }" size="small" bordered style="margin-bottom:20px">
            <a-descriptions-item label="客户姓名">{{ drawerItinerary.customer_name }}</a-descriptions-item>
            <a-descriptions-item label="联系电话">{{ drawerItinerary.customer_phone }}</a-descriptions-item>
            <a-descriptions-item label="出行人数">{{ drawerItinerary.pax }} 人</a-descriptions-item>
            <a-descriptions-item label="目的地">{{ drawerItinerary.destination }}</a-descriptions-item>
            <a-descriptions-item label="出发日期">{{ drawerItinerary.start_date }}</a-descriptions-item>
            <a-descriptions-item label="结束日期">{{ drawerItinerary.end_date }}</a-descriptions-item>
            <a-descriptions-item v-if="drawerItinerary.travelers" label="出行人员" :span="2">{{ drawerItinerary.travelers }}</a-descriptions-item>
          </a-descriptions>
          <a-divider orientation="left" style="margin-top:0">每日行程</a-divider>
          <a-collapse v-if="drawerItinerary.days_detail?.length" :activeKey="drawerCollapseKeys">
            <a-collapse-panel
              v-for="day in drawerItinerary.days_detail"
              :key="day.seq"
              :header="`第 ${day.seq} 天 · ${day.date ?? ''}`"
            >
              <p style="white-space:pre-wrap;margin:0">{{ day.details }}</p>
              <p v-if="day.accommodation_area" style="color:#888;margin:6px 0 0">🏨 住宿：{{ day.accommodation_area }}</p>
              <p v-if="day.notes" style="color:#888;margin:4px 0 0">📌 备注：{{ day.notes }}</p>
            </a-collapse-panel>
          </a-collapse>
          <a-empty v-else description="暂无每日行程" />
        </template>
      </a-spin>
    </a-drawer>

    <!-- 编辑/新建行程抽屉 -->
    <a-drawer
      :title="editingId ? '编辑行程' : '新建行程'"
      :open="drawerOpen"
      :width="isMobile ? '100%' : drawerWidth"
      placement="right"
      :destroy-on-close="true"
      @close="drawerOpen = false"
    >
      <ItineraryFormView
        ref="itineraryFormRef"
        :edit-id="editingId"
        :show-footer="false"
        @saved="onSaved"
        @cancel="drawerOpen = false"
      />
      <template #footer>
        <a-space style="width:100%;justify-content:flex-end">
          <a-button @click="drawerOpen = false">取消</a-button>
          <a-button type="primary" :loading="itineraryFormRef?.loading" @click="itineraryFormRef?.handleSubmit()">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
