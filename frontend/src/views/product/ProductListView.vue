<script setup lang="ts">
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { FilterOutlined } from '@ant-design/icons-vue'
import { productApi } from '@/api/product'
import type { Product, ProductListItem } from '@/types'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const products = ref<ProductListItem[]>([])
const loading = ref(false)
const query = reactive({ keyword: '', status: 'enabled' as string | undefined })
const pagination = reactive({ current: 1, pageSize: 10, total: 0 })
const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<Product>>({ status: 'enabled', itinerary_template: [] })

const drawerViewOpen = ref(false)
const drawerViewData = ref<Product | null>(null)
const drawerLoading = ref(false)
const productViewCollapseKeys = computed(() =>
  drawerViewData.value?.itinerary_template?.map(d => d.seq) ?? []
)

let daysWatchTimer: ReturnType<typeof setTimeout> | null = null

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await productApi.list({ ...query, page: pagination.current, page_size: pagination.pageSize })
  const d = (res.data as any)
  if (d?.items) {
    products.value = d.items
    pagination.total = d.total ?? d.items.length
  } else {
    products.value = d ?? []
    pagination.total = products.value.length
  }
  loading.value = false
}

function openCreate() {
  editingId.value = null
  form.value = { status: 'enabled', itinerary_template: [] }
  drawerOpen.value = true
}

async function openEdit(id: number) {
  try {
    const res = await productApi.get(id)
    if (!res?.data?.id) { message.error('获取产品数据失败'); return }
    editingId.value = id
    const d = res.data ?? {}
    form.value = {
      ...d,
      price: d.price ?? undefined,
      includes: d.includes ?? undefined,
      excludes: d.excludes ?? undefined,
      cancellation_policy: d.cancellation_policy ?? undefined,
      travel_notice: d.travel_notice ?? undefined,
      important_tips: d.important_tips ?? undefined,
      remark: d.remark ?? undefined,
      itinerary_template: (d.itinerary_template ?? []).map((day: any) => ({
        ...day,
        accommodation_area: day.accommodation_area ?? undefined,
        notes: day.notes ?? undefined,
      })),
    }
    drawerOpen.value = true
  } catch {
    message.error('获取产品数据失败')
  }
}

function addTemplateDay() {
  const days = form.value.itinerary_template ?? []
  form.value.itinerary_template = [...days, { seq: days.length + 1, details: '', accommodation_area: undefined, notes: undefined }]
}

function syncItineraryTodays(newDays: number) {
  const count = Math.min(Math.floor(newDays), 30)
  if (count < 1) return
  const current = form.value.itinerary_template ?? []
  if (current.some((d: any) => d.details?.trim())) return
  if (count > current.length) {
    const extra = Array.from({ length: count - current.length }, (_, i) => ({
      seq: current.length + i + 1,
      details: '',
      accommodation_area: undefined,
      notes: undefined,
    }))
    form.value.itinerary_template = [...current, ...extra]
  } else if (count < current.length) {
    form.value.itinerary_template = current.slice(0, count)
  }
  if (newDays > 30) {
    message.warning('天数超过上限，已自动生成 30 天行程模板')
  }
}

watch(() => form.value.days, (newVal) => {
  if (daysWatchTimer) clearTimeout(daysWatchTimer)
  daysWatchTimer = setTimeout(() => syncItineraryTodays(newVal ?? 0), 400)
})

function removeTemplateDay(index: number) {
  const days = [...(form.value.itinerary_template ?? [])]
  days.splice(index, 1)
  form.value.itinerary_template = days.map((d, i) => ({ ...d, seq: i + 1 }))
}

async function save() {
  if (!form.value.name?.trim()) { message.error('请输入产品名称'); return }
  if (!form.value.destination?.trim()) { message.error('请输入目的地'); return }
  if (!form.value.days || form.value.days < 1) { message.error('请输入正确的天数'); return }
  if (!form.value.price || form.value.price < 0) { message.error('请输入正确的价格'); return }

  const payload = { ...form.value } as any
  try {
    if (editingId.value) {
      await productApi.update(editingId.value, payload)
    } else {
      await productApi.create(payload)
    }
  } catch {
    message.error('保存失败，请稍后重试')
    return
  }
  drawerOpen.value = false
  message.success('保存成功')
  fetchList()
}

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerViewData.value = null
  drawerLoading.value = true
  try {
    const res = await productApi.get(id)
    drawerViewData.value = res.data
  } catch {
    message.error('加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function toggleStatus(record: any) {
  const next = record.status === 'enabled' ? 'disabled' : 'enabled'
  await productApi.update(record.id, { status: next })
  message.success(next === 'enabled' ? '已启用' : '已禁用')
  fetchList()
}

const mobileFilterOpen = ref(false)
const mobileFilter = reactive({ keyword: '', status: 'enabled' as string | undefined })

const activeFilterCount = computed(() => {
  let n = 0
  if (query.keyword) n++
  if (query.status !== 'enabled') n++
  return n
})

function openMobileFilter() {
  mobileFilter.keyword = query.keyword
  mobileFilter.status = query.status
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  query.keyword = mobileFilter.keyword
  query.status = mobileFilter.status
  pagination.current = 1
  mobileFilterOpen.value = false
  fetchList()
}

function resetMobileFilter() {
  mobileFilter.keyword = ''
  mobileFilter.status = 'enabled'
}

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '产品名称', dataIndex: 'name', width: 200, ellipsis: true },
  { title: '目的地', dataIndex: 'destination', width: 130, ellipsis: true },
  { title: '天数', dataIndex: 'days', width: 60, align: 'center' as const },
  { title: '价格(元)', dataIndex: 'price', width: 110, align: 'right' as const,
    customRender: ({ text }: any) => text != null ? `¥${Number(text).toLocaleString()}` : '-' },
  { title: '状态', dataIndex: 'status', width: 70, align: 'center' as const },
  { title: '操作', key: 'action', width: 180, fixed: 'right' as const },
]
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <!-- 桌面端筛选表单?-->
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="名称">
          <a-input v-model:value="query.keyword" placeholder="搜索产品名称" allow-clear @change="() => { pagination.current = 1; fetchList() }" style="width:180px" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="query.status" placeholder="全部" allow-clear style="width:90px" @change="() => { pagination.current = 1; fetchList() }">
            <a-select-option value="enabled">启用</a-select-option>
            <a-select-option value="disabled">禁用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="() => { query.keyword = ''; query.status = 'enabled'; pagination.current = 1; fetchList() }">重置</a-button>
        </a-form-item>
      </a-form>
      <!-- 移动端筛选按钮?-->
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter"><template #icon><filter-outlined /></template>筛选</a-button>
      </a-badge>
      <a-button type="primary" @click="openCreate">新增产品</a-button>
    </div>

    <!-- 移动端卡片?-->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="products" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;color:#111827;font-size:14px">{{ record.name }}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">{{ record.destination }} · {{ record.days }}天</div>
                    <div v-if="record.price" style="font-size:12px;color:#0d9488;margin-top:2px">¥{{ Number(record.price).toLocaleString() }}</div>
                  </div>
                  <a-tag :color="record.status === 'enabled' ? 'green' : 'default'" style="margin:0">{{ record.status === 'enabled' ? '启用' : '禁用' }}</a-tag>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:8px">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button size="small" @click="openEdit(record.id)">编辑</a-button>
                  <a-button size="small" :type="record.status === 'enabled' ? 'default' : 'primary'" @click="toggleStatus(record)">{{ record.status === 'enabled' ? '禁用' : '启用' }}</a-button>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
        <div style="display:flex;justify-content:center;margin-top:12px">
          <a-pagination :total="pagination.total" :current="pagination.current" :page-size="pagination.pageSize" size="small" :show-size-changer="false"
            @change="(p: number) => { pagination.current = p; fetchList() }" />
        </div>
      </a-spin>
    </template>

    <!-- 桌面端表格?-->
    <a-table v-else
      :data-source="products"
      :columns="columns"
      :loading="loading"
      :scroll="{ x: 800 }"
      :pagination="{ current: pagination.current, pageSize: pagination.pageSize, total: pagination.total, showSizeChanger: true, showTotal: (t: number) => `共 ${t} 条` }"
      row-key="id"
      size="middle"
      @change="(p: any) => { pagination.current = p.current; pagination.pageSize = p.pageSize; fetchList() }"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ index + 1 }}</template>
        <template v-else-if="column.dataIndex === 'status'">
          <a-tag :color="record.status === 'enabled' ? 'green' : 'default'">
            {{ record.status === 'enabled' ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button size="small" @click="openEdit(record.id)">编辑</a-button>
            <a-button size="small" :type="record.status === 'enabled' ? 'default' : 'primary'" @click="toggleStatus(record)">
              {{ record.status === 'enabled' ? '禁用' : '启用' }}
            </a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉?-->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="50vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="名称"><a-input v-model:value="mobileFilter.keyword" placeholder="搜索产品名称" allow-clear /></a-form-item>
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
      title="产品详情"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : 620"
      placement="right"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerViewData">
          <a-descriptions :column="1" bordered size="small" style="margin-bottom:16px">
            <a-descriptions-item label="产品名称">{{ drawerViewData.name }}</a-descriptions-item>
            <a-descriptions-item label="出发地">{{ drawerViewData.origin ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="目的地">{{ drawerViewData.destination }}</a-descriptions-item>
            <a-descriptions-item label="天数">{{ drawerViewData.days }} 天</a-descriptions-item>
            <a-descriptions-item label="价格">
              {{ drawerViewData.price != null ? `¥${Number(drawerViewData.price).toLocaleString()}` : '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="drawerViewData.status === 'enabled' ? 'green' : 'default'">{{ drawerViewData.status === 'enabled' ? '启用' : '禁用' }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item v-if="drawerViewData.includes" label="费用包含">
              <span style="white-space:pre-wrap">{{ drawerViewData.includes }}</span>
            </a-descriptions-item>
            <a-descriptions-item v-if="drawerViewData.excludes" label="费用不含">
              <span style="white-space:pre-wrap">{{ drawerViewData.excludes }}</span>
            </a-descriptions-item>
            <a-descriptions-item v-if="drawerViewData.remark" label="备注">
              <span style="white-space:pre-wrap">{{ drawerViewData.remark }}</span>
            </a-descriptions-item>
          </a-descriptions>
          <template v-if="drawerViewData.itinerary_template?.length">
            <div style="font-weight:600;margin-bottom:8px">行程模板</div>
            <a-collapse :bordered="false" :activeKey="productViewCollapseKeys">
              <a-collapse-panel v-for="day in drawerViewData.itinerary_template" :key="day.seq" :header="`第${day.seq}天${day.accommodation_area ? ' · ' + day.accommodation_area : ''}`">
                <p style="white-space:pre-wrap;margin:0">{{ day.details || '-' }}</p>
                <p v-if="day.notes" style="color:#9ca3af;font-size:12px;margin:4px 0 0">备注：{{ day.notes }}</p>
              </a-collapse-panel>
            </a-collapse>
          </template>
        </template>
      </a-spin>
    </a-drawer>

    <!-- 表单抽屉 -->
    <a-drawer
      :title="editingId ? '编辑产品' : '新增产品'"
      :open="drawerOpen"
      :width="isMobile ? '100%' : 620"
      placement="right"
      @close="drawerOpen = false"
    >
      <a-form layout="vertical">
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="产品名称" required>
              <a-input v-model:value="form.name" placeholder="请输入产品名称" />
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="出发地">
              <a-input v-model:value="form.origin" placeholder="如：北京" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="目的地" required>
              <a-input v-model:value="form.destination" placeholder="如：桂林" />
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="天数" required>
              <a-input-number v-model:value="form.days" :min="1" :max="365" style="width:100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 24">
            <a-form-item label="价格（元）" required>
              <a-input-number v-model:value="form.price" :min="0" :precision="2" style="width:100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="费用包含">
          <a-textarea v-model:value="form.includes" :rows="2" placeholder="包含的费用项目" />
        </a-form-item>
        <a-form-item label="费用不含">
          <a-textarea v-model:value="form.excludes" :rows="2" placeholder="不含的费用项目" />
        </a-form-item>
        <a-form-item label="取消政策">
          <a-textarea v-model:value="form.cancellation_policy" :rows="2" placeholder="退改政策说明" />
        </a-form-item>
        <a-form-item label="出行提示">
          <a-textarea v-model:value="form.travel_notice" :rows="2" placeholder="集合地点、携带物品等" />
        </a-form-item>
        <a-form-item label="重要提示">
          <a-textarea v-model:value="form.important_tips" :rows="2" placeholder="注意事项、禁忌等" />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="form.remark" :rows="2" />
        </a-form-item>

        <!-- 行程模板 -->
        <a-divider>行程模板</a-divider>
        <div v-for="(day, idx) in (form.itinerary_template ?? [])" :key="idx"
          style="margin-bottom:12px;border:1px solid #f0f0f0;border-radius:6px;padding:10px">
          <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px">
            <span style="min-width:48px;color:#666;font-size:13px;font-weight:500">第{{ day.seq }}天</span>
            <a-button size="small" danger @click="removeTemplateDay(idx)">删除</a-button>
          </div>
          <a-textarea v-model:value="day.details" :rows="2" placeholder="当天行程内容" style="margin-bottom:6px" />
          <a-row :gutter="8">
            <a-col :span="isMobile ? 24 : 12">
              <a-input v-model:value="day.accommodation_area" placeholder="住宿区域（选填）" />
            </a-col>
            <a-col :span="isMobile ? 24 : 12">
              <a-input v-model:value="day.notes" placeholder="备注（选填）" />
            </a-col>
          </a-row>
        </div>
        <a-button type="dashed" style="width:100%;margin-top:4px" @click="addTemplateDay">+ 添加一天</a-button>
      </a-form>

      <template #footer>
        <a-space style="width:100%;justify-content:flex-end">
          <a-button @click="drawerOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
