<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { itineraryApi } from '@/api/itinerary'
import type { Itinerary } from '@/types'

const route = useRoute()
const itinerary = ref<Itinerary | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const STATUS_LABEL: Record<string, string> = {
  not_started: '未开始', in_progress: '进行中', completed: '已完成',
}
const STATUS_COLOR: Record<string, string> = {
  not_started: 'default', in_progress: 'processing', completed: 'success',
}

const collapseKeys = computed(() =>
  itinerary.value?.days_detail?.map(d => d.seq) ?? []
)

onMounted(async () => {
  const token = route.params.token as string
  try {
    const res = await itineraryApi.getPublicItinerary(token)
    if (!res.data) {
      error.value = '分享链接无效或已失效'
      return
    }
    itinerary.value = res.data
  } catch {
    error.value = '分享链接无效或已失效'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div style="padding:16px 12px;max-width:860px;margin:0 auto">
    <a-page-header title="行程详情" style="padding:0 0 12px" />
    <a-spin :spinning="loading">
      <template v-if="itinerary">
        <!-- 标题行 -->
        <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap">
          <span style="font-size:16px;font-weight:600">{{ itinerary.customer_name }} · {{ itinerary.destination }}</span>
          <a-tag :color="STATUS_COLOR[itinerary.status]">{{ STATUS_LABEL[itinerary.status] }}</a-tag>
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
        <a-empty v-else description="暂无每日行程" style="margin-bottom:20px" />
      </template>
      <a-empty v-else-if="!loading" :description="error ?? '行程不存在'" />
    </a-spin>
  </div>
</template>
