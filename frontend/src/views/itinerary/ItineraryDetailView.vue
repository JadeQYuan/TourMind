<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import { itineraryApi } from '@/api/itinerary'
import type { Itinerary } from '@/types'

interface ServiceOrder {
  id: number
  service_type: string
  amount: number
  order_date: string
  status: string
  notes: string | null
  supplier_id: number | null
}

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)
const isPublic = ref(false)

const itinerary = ref<Itinerary | null>(null)
const orders = ref<ServiceOrder[]>([])
const loading = ref(true)

const STATUS_LABEL: Record<string, string> = {
  not_started: '未开始', in_progress: '进行中', completed: '已完成', cancelled: '已撤销',
}
const STATUS_COLOR: Record<string, string> = {
  not_started: 'default', in_progress: 'processing', completed: 'success', cancelled: 'error',
}

const error = ref<string | null>(null)

const collapseKeys = computed(() =>
  itinerary.value?.days_detail?.map(d => d.seq) ?? []
)

onMounted(async () => {
  const token = route.params.token as string | undefined
  try {
    if (token) {
      isPublic.value = true
      const iRes = await itineraryApi.getPublicItinerary(token)
      if (!iRes.data) {
        error.value = '分享链接无效或已失效'
        return
      }
      itinerary.value = iRes.data
    } else {
      const [iRes, oRes] = await Promise.all([itineraryApi.get(id), itineraryApi.listOrders(id)])
      itinerary.value = iRes.data
      orders.value = (oRes.data ?? []) as unknown as ServiceOrder[]
    }
  } catch {
    error.value = isPublic.value ? '分享链接无效或已失效' : '行程加载失败'
  } finally {
    loading.value = false
  }
})

async function changeStatus(status: string) {
  await itineraryApi.patchStatus(id, status)
  const res = await itineraryApi.get(id)
  itinerary.value = res.data
  message.success('状态已更新')
}

function doMarkComplete() {
  changeStatus('completed')
}

function doCancelItinerary() {
  Modal.confirm({
    title: '撤销行程',
    content: '确认撤销该行程？撤销后状态不可恢复，行程将标记为"已撤销"。',
    okText: '确认撤销',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => changeStatus('cancelled'),
  })
}

const orderColumns = [
  { title: '服务类型', dataIndex: 'service_type' },
  { title: '金额(元)', dataIndex: 'amount', customRender: ({ text }: any) => `¥${text}` },
  { title: '服务日期', dataIndex: 'order_date' },
  { title: '状态', dataIndex: 'status' },
]
</script>

<template>
  <div style="padding:16px 12px;max-width:860px;margin:0 auto">
    <a-page-header
      title="行程详情"
      v-bind="isPublic ? {} : { onBack: () => router.back() }"
      style="padding:0 0 12px"
    />
    <a-spin :spinning="loading">
      <template v-if="itinerary">
        <!-- 客户 & 状态标题行 -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap">
          <span style="font-size:16px;font-weight:600">{{ itinerary.customer_name }} · {{ itinerary.destination }}</span>
          <a-tag :color="STATUS_COLOR[itinerary.status]">{{ STATUS_LABEL[itinerary.status] }}</a-tag>
        </div>

        <!-- 操作区 -->
        <div v-if="!isPublic" style="margin-bottom:20px">
          <a-space wrap>
            <a-button v-if="itinerary.status === 'not_started'" type="primary" @click="changeStatus('in_progress')">开始执行</a-button>
            <a-button v-if="itinerary.status === 'in_progress' && dayjs().isAfter(dayjs(itinerary.end_date), 'day')" type="primary" @click="doMarkComplete()">标记完成</a-button>
            <a-button v-if="['not_started','in_progress'].includes(itinerary.status) && !dayjs().isAfter(dayjs(itinerary.end_date), 'day')" danger @click="doCancelItinerary()">撤销行程</a-button>
            <a-button v-if="itinerary.status !== 'cancelled'" @click="router.push(`/itineraries/${id}/edit`)">编辑</a-button>
          </a-space>
        </div>

        <!-- 基本信息 -->
        <a-divider orientation="left" style="margin-top:0">基本信息</a-divider>
        <a-descriptions :column="{ xs: 1, sm: 2, md: 3 }" size="small" style="margin-bottom:20px" bordered>
          <a-descriptions-item label="客户姓名">{{ itinerary.customer_name }}</a-descriptions-item>
          <a-descriptions-item label="联系电话">{{ itinerary.customer_phone }}</a-descriptions-item>
          <a-descriptions-item label="出行人数">{{ itinerary.pax }} 人</a-descriptions-item>
          <a-descriptions-item label="目的地">{{ itinerary.destination }}</a-descriptions-item>
          <a-descriptions-item label="出发日期">{{ itinerary.start_date }}</a-descriptions-item>
          <a-descriptions-item label="结束日期">{{ itinerary.end_date }}</a-descriptions-item>
          <a-descriptions-item v-if="itinerary.travelers" label="出行人员" :span="3">
            {{ itinerary.travelers }}
          </a-descriptions-item>
        </a-descriptions>

        <!-- 每日行程 -->
        <a-divider orientation="left">每日行程</a-divider>
        <a-collapse v-if="itinerary.days_detail?.length" :activeKey="collapseKeys" style="margin-bottom:20px">
          <a-collapse-panel
            v-for="day in itinerary.days_detail"
            :key="day.seq"
            :header="`第 ${day.seq} 天 · ${day.date ?? ''}`"
          >
            <p style="white-space:pre-wrap;margin:0">{{ day.details }}</p>
            <p v-if="day.accommodation_area" style="color:#888;margin:6px 0 0">🏨 住宿：{{ day.accommodation_area }}</p>
            <p v-if="day.notes" style="color:#888;margin:4px 0 0">📌 备注：{{ day.notes }}</p>
          </a-collapse-panel>
        </a-collapse>
        <a-empty v-else-if="!itinerary.days_detail?.length" description="暂无每日行程" style="margin-bottom:20px" />

        <!-- 服务安排 -->
        <div v-if="!isPublic">
          <a-divider orientation="left">服务安排</a-divider>
          <a-table :data-source="orders" :columns="orderColumns" :pagination="false" row-key="id" size="small" :locale="{ emptyText: '暂无服务安排' }" style="margin-bottom:20px">
            <template #bodyCell="{ column, record }">
              <template v-if="column.dataIndex === 'status'">
                <a-tag :color="record.status === 'confirmed' ? 'blue' : record.status === 'cancelled' ? 'red' : 'default'">
                  {{ record.status === 'confirmed' ? '已确认' : record.status === 'cancelled' ? '已取消' : '待确认' }}
                </a-tag>
              </template>
            </template>
          </a-table>
        </div>
      </template>
      <a-empty v-else-if="!loading" :description="error ?? '行程不存在'" />
    </a-spin>
  </div>
</template>
