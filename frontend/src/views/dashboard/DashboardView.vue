<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { dashboardApi } from '@/api/dashboard'
import type { DashboardResponse } from '@/types'
import * as echarts from 'echarts'

const data = ref<DashboardResponse | null>(null)
const loading = ref(true)
const dateRange = ref<[string, string] | null>(null)

const chartRefs: Record<string, HTMLElement | null> = {}
const chartInstances: echarts.ECharts[] = []

function setRef(key: string) {
  return (el: any) => { chartRefs[key] = el as HTMLElement | null }
}

const PALETTE = ['#1677ff', '#13c2c2', '#52c41a', '#fa8c16', '#722ed1', '#eb2f96', '#faad14', '#f5222d']

function makePie(seriesData: { name: string; value: number }[], name: string): echarts.EChartsOption {
  return {
    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
    legend: { bottom: 0, type: 'scroll', textStyle: { fontSize: 12 } },
    color: PALETTE,
    series: [{
      name, type: 'pie', radius: ['38%', '65%'], center: ['50%', '42%'],
      data: seriesData, label: { show: false },
      emphasis: { label: { show: true, fontSize: 13, fontWeight: 'bold' } },
    }],
  }
}

function makeLine(trend: { month: string; income: number; expense: number; profit: number }[]): echarts.EChartsOption {
  return {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => params.map((p: any) => `${p.marker}${p.seriesName}: ¥${Number(p.value).toLocaleString()}`).join('<br/>'),
    },
    legend: { data: ['收入', '支出', '利润'], bottom: 0 },
    color: ['#1677ff', '#f5222d', '#52c41a'],
    grid: { top: 20, bottom: 50, left: 60, right: 20 },
    xAxis: { type: 'category', data: trend.map(t => t.month), axisLabel: { fontSize: 11 } },
    yAxis: { type: 'value', axisLabel: { formatter: (v: number) => `¥${(v / 1000).toFixed(0)}k`, fontSize: 11 } },
    series: [
      { name: '收入', type: 'line', smooth: true, data: trend.map(t => t.income), areaStyle: { opacity: .08 } },
      { name: '支出', type: 'line', smooth: true, data: trend.map(t => t.expense), areaStyle: { opacity: .08 } },
      { name: '利润', type: 'line', smooth: true, data: trend.map(t => t.profit), areaStyle: { opacity: .08 } },
    ],
  }
}

const ORDER_STATUS_LABEL: Record<string, string> = {
  pending_deposit: '待定金', pending_payment: '待尾款', completed: '已完成', cancelled: '已取消',
}

function initCharts() {
  const d = data.value
  if (!d) return

  const trend = d.monthly_income_trend ?? []
  const topProductsPie = (d.top_products ?? []).map(p => ({ name: p.product_name, value: p.order_count }))
  const topSuppliersPie = (d.top_suppliers ?? []).map(s => ({ name: s.supplier_name, value: s.total_cost }))
  const statusPie = (d.order_status_distribution ?? []).map(s => ({
    name: ORDER_STATUS_LABEL[s.status] ?? s.status, value: s.count,
  }))

  const defs: [string, echarts.EChartsOption][] = [
    ['monthlyTrend', makeLine(trend)],
    ['topProducts', makePie(topProductsPie, '订单数')],
    ['topSuppliers', makePie(topSuppliersPie, '成本')],
    ['orderStatus', makePie(statusPie, '订单状态')],
  ]

  for (const [key, option] of defs) {
    const el = chartRefs[key]
    if (!el) continue
    const inst = echarts.init(el, undefined, { renderer: 'canvas' })
    inst.setOption(option)
    chartInstances.push(inst)
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = dateRange.value
      ? { start_date: dateRange.value[0], end_date: dateRange.value[1] }
      : undefined
    const res = await dashboardApi.get(params)
    data.value = res.data
  } catch (e) {
    console.error('[Dashboard] API error:', e)
  } finally {
    loading.value = false
  }
  await new Promise(r => setTimeout(r, 50))
  chartInstances.forEach(c => c.dispose())
  chartInstances.length = 0
  initCharts()
}

function handleResize() {
  chartInstances.forEach(c => c.resize())
}

onMounted(() => {
  loadData()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstances.forEach(c => c.dispose())
})
</script>

<template>
  <div style="padding:24px">
    <a-spin :spinning="loading">
      <!-- Date range filter -->
      <div style="margin-bottom:16px;display:flex;align-items:center;gap:12px">
        <span style="font-size:14px;color:#666">日期范围：</span>
        <a-range-picker
          value-format="YYYY-MM-DD"
          style="width:240px"
          @change="(dates: string[]) => { dateRange = dates?.length === 2 ? [dates[0], dates[1]] : null; loadData() }"
        />
      </div>

      <!-- KPI Cards -->
      <a-row :gutter="[16, 16]" style="margin-bottom:16px" v-if="data">
        <a-col :xs="12" :sm="6">
          <a-card :body-style="{padding:'16px'}" style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <a-statistic title="总订单数" :value="data.summary.total_orders" />
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-card :body-style="{padding:'16px'}" style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <a-statistic title="总收入" :value="data.summary.total_income" prefix="¥" :precision="2" :value-style="{ color: '#52c41a' }" />
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-card :body-style="{padding:'16px'}" style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <a-statistic title="总支出" :value="data.summary.total_expense" prefix="¥" :precision="2" :value-style="{ color: '#f5222d' }" />
          </a-card>
        </a-col>
        <a-col :xs="12" :sm="6">
          <a-card :body-style="{padding:'16px'}" style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <a-statistic title="总利润" :value="data.summary.total_profit" prefix="¥" :precision="2" :value-style="{ color: '#1677ff' }" />
          </a-card>
        </a-col>
      </a-row>

      <!-- Trend chart -->
      <a-card title="收支趋势（近6个月）" :body-style="{padding:'12px 16px'}"
        style="margin-bottom:16px;border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
        <div :ref="setRef('monthlyTrend')" style="height:240px" />
      </a-card>

      <a-row :gutter="[16, 16]" style="margin-bottom:16px">
        <a-col :xs="24" :sm="8">
          <a-card title="订单状态分布" :body-style="{padding:'12px 8px'}"
            style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <div :ref="setRef('orderStatus')" style="height:220px" />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="8">
          <a-card title="热销产品 TOP5" :body-style="{padding:'12px 8px'}"
            style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <div :ref="setRef('topProducts')" style="height:220px" />
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="8">
          <a-card title="主要供应商成本 TOP5" :body-style="{padding:'12px 8px'}"
            style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)">
            <div :ref="setRef('topSuppliers')" style="height:220px" />
          </a-card>
        </a-col>
      </a-row>

      <!-- Recent orders table -->
      <a-card title="最近订单" :body-style="{padding:'12px 16px'}"
        style="border-radius:12px;border:none;box-shadow:0 2px 12px rgba(0,0,0,.06)" v-if="data">
        <a-table
          :data-source="data.recent_orders"
          :columns="[
            { title: '订单号', dataIndex: 'order_no', width: 180 },
            { title: '客户', dataIndex: 'customer_name', width: 90 },
            { title: '产品', dataIndex: 'product_name' },
            { title: '金额', dataIndex: 'total_price', width: 110, align: 'right', customRender: ({ text }: any) => text ? `¥${Number(text).toLocaleString()}` : '—' },
            { title: '状态', dataIndex: 'status', width: 90, customRender: ({ text }: any) => text },
          ]"
          row-key="id"
          :pagination="false"
          size="small"
        />
      </a-card>
    </a-spin>
  </div>
</template>
