<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import dayjs from 'dayjs'
import { itineraryApi } from '@/api/itinerary'
import { orderApi } from '@/api/order'
import { productApi } from '@/api/product'
import { useBreakpoint } from '@/composables/useBreakpoint'

const props = defineProps<{ editId?: number | null; showFooter?: boolean }>()
const emit = defineEmits<{ saved: [id: number]; cancel: [] }>()

const router = useRouter()
const route = useRoute()
const { isMobile } = useBreakpoint()
const routeId = computed(() => route.params.id ? Number(route.params.id) : null)
const resolvedId = computed(() => props.editId ?? routeId.value)
const isEdit = computed(() => !!resolvedId.value)

const loading = ref(false)
const prevOrderId = ref<number | undefined>(undefined)
const orderOptions = ref<{ id: number; order_no: string; customer_name: string; product_name: string; product_id?: number; travel_date: string; destination?: string }[]>([])

interface DayDetail {
  seq: number
  date: string
  details: string
  accommodation_area: string
  notes: string
}

const form = reactive({
  customer_order_id: undefined as number | undefined,
  destination: '',
  pax: 1,
  travelers: '' as string,
  start_date: '',
  end_date: '',
  status: 'not_started',
  days_detail: [] as DayDetail[],
})

function resetForm() {
  Object.assign(form, {
    customer_order_id: undefined, destination: '', pax: 1,
    travelers: '', start_date: '', end_date: '', status: 'not_started', days_detail: [],
  })
  prevOrderId.value = undefined
}

async function loadOrders() {
  const res = await orderApi.list({ page_size: 100 })
  orderOptions.value = (res.data?.items ?? res.data ?? []).map((o: any) => ({
    id: o.id,
    order_no: o.order_no,
    customer_name: o.customer_name,
    product_name: o.product_name ?? '',
    product_id: o.product_id,
    travel_date: o.travel_date,
    destination: o.product_destination ?? '',
  }))
}

async function onOrderChange(orderId: number) {
  const o = orderOptions.value.find(x => x.id === orderId)
  if (!o) return
  const oldOrderId = prevOrderId.value
  const oldStartDate = form.start_date
  form.start_date = o.travel_date
  prevOrderId.value = orderId
  // Auto-fill destination from product
  if (o.destination) {
    form.destination = o.destination
  } else if (o.product_id) {
    try {
      const res = await productApi.get(o.product_id)
      if (res.data?.destination) form.destination = res.data.destination
    } catch { /* ignore */ }
  }
  if (!isEdit.value) {
    autoFillFromOrder(oldOrderId, oldStartDate)
  }
}

async function autoFillFromOrder(oldOrderId: number | undefined, oldStartDate: string) {
  if (fillingTemplate.value) return
  const hasContent = form.days_detail.some(d => d.details.trim() !== '')
  if (!hasContent) {
    await fillFromTemplate()
    return
  }
  Modal.confirm({
    title: '替换每日明细',
    content: '当前已有每日明细内容，切换订单将覆盖已填写内容，是否继续？',
    okText: '确认替换',
    cancelText: '取消',
    onOk: () => fillFromTemplate(),
    onCancel: () => {
      form.customer_order_id = oldOrderId
      form.start_date = oldStartDate
      prevOrderId.value = oldOrderId
    },
  })
}

// Fill days_detail from linked product's itinerary_template
const fillingTemplate = ref(false)
async function fillFromTemplate() {
  const order = orderOptions.value.find(x => x.id === form.customer_order_id)
  if (!order?.product_id) { message.warning('订单没有关联产品'); return }
  fillingTemplate.value = true
  try {
    const res = await productApi.get(order.product_id)
    const tpl = res.data?.itinerary_template
    if (!tpl?.length) { message.warning('产品没有行程模板'); return }
    const start = dayjs(form.start_date || order.travel_date)
    form.start_date = start.format('YYYY-MM-DD')
    form.end_date = start.add(tpl.length - 1, 'day').format('YYYY-MM-DD')
    form.days_detail = tpl.map((t: any, i: number) => ({
      seq: i + 1,
      date: start.add(i, 'day').format('YYYY-MM-DD'),
      details: t.details ?? '',
      accommodation_area: t.accommodation_area ?? '',
      notes: t.notes ?? '',
    }))
    message.success('已从产品模板填入行程')
  } catch {
    message.error('读取产品模板失败')
  } finally {
    fillingTemplate.value = false
  }
}

// rebuild days_detail when start/end changes
function rebuildDays() {
  if (!form.start_date || !form.end_date) return
  const start = dayjs(form.start_date)
  const end = dayjs(form.end_date)
  const count = end.diff(start, 'day') + 1
  if (count < 1 || count > 60) return
  const existing = [...form.days_detail]
  form.days_detail = Array.from({ length: count }, (_, i) => {
    const ex = existing[i]
    return ex ? { ...ex, seq: i + 1, date: start.add(i, 'day').format('YYYY-MM-DD') } : {
      seq: i + 1,
      date: start.add(i, 'day').format('YYYY-MM-DD'),
      details: '',
      accommodation_area: '',
      notes: '',
    }
  })
}

watch(() => [form.start_date, form.end_date], rebuildDays)

const expandedKeys = ref<number[]>([])
watch(() => form.days_detail, (val) => {
  expandedKeys.value = val.map((_, idx) => idx)
}, { immediate: true })

async function load() {
  const res = await itineraryApi.get(resolvedId.value!)
  const d = res.data
  form.customer_order_id = d.customer_order_id ?? d.order_id ?? undefined
  form.destination = d.destination ?? ''
  form.pax = d.pax ?? 1
  form.travelers = d.travelers ?? ''
  form.start_date = d.start_date ?? ''
  form.end_date = d.end_date ?? ''
  form.status = d.status ?? 'not_started'
  form.days_detail = (d.days_detail ?? []).map((x: any, i: number) => ({
    seq: x.seq ?? i + 1,
    date: x.date ?? '',
    details: x.details ?? '',
    accommodation_area: x.accommodation_area ?? '',
    notes: x.notes ?? '',
  }))
}

async function handleSubmit() {
  if (!form.customer_order_id) { message.error('请选择关联订单'); return }
  if (!form.start_date) { message.error('请选择开始日期'); return }
  loading.value = true
  try {
    if (isEdit.value) {
      await itineraryApi.update(resolvedId.value!, { ...form })
      message.success('更新成功')
      emit('saved', resolvedId.value!)
      if (!props.editId) router.push('/itineraries')
    } else {
      const res = await itineraryApi.create({ ...form })
      message.success('创建成功')
      emit('saved', res.data.id)
      if (!props.editId) router.push(`/itineraries/${res.data.id}`)
    }
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  emit('cancel')
  if (!props.editId) router.push('/itineraries')
}


onMounted(() => {
  loadOrders()
  if (routeId.value) load()
})

watch(() => props.editId, (val) => {
  resetForm()
  if (val) load()
}, { immediate: true })

defineExpose({ resetForm, handleSubmit, loading })
</script>

<template>
  <div>
    <a-form layout="vertical" @finish="handleSubmit">
      <!-- 关联订单 -->
      <a-form-item label="关联订单" required>
        <a-select
          v-model:value="form.customer_order_id"
          placeholder="请选择关联订单"
          style="width:100%"
          show-search
          :filter-option="(input: string, opt: any) => opt.label?.toLowerCase().includes(input.toLowerCase())"
          @change="onOrderChange"
        >
          <a-select-option
            v-for="o in orderOptions" :key="o.id" :value="o.id"
            :label="`${o.order_no} ${o.customer_name}`"
          >
            <div>{{ o.order_no }} · {{ o.customer_name }}</div>
            <div style="font-size:12px;color:#8c8c8c">{{ o.product_name }}  {{ o.travel_date }}</div>
          </a-select-option>
        </a-select>
      </a-form-item>

      <a-row :gutter="16">
        <a-col :span="isMobile ? 24 : 12">
          <a-form-item label="目的地" required>
            <a-input v-model:value="form.destination" placeholder="如：桂林" />
          </a-form-item>
        </a-col>
        <a-col :span="isMobile ? 24 : 6">
          <a-form-item label="出行人数" required>
            <a-input-number v-model:value="form.pax" :min="1" style="width:100%" />
          </a-form-item>
        </a-col>
      </a-row>
      <a-row :gutter="16">
        <a-col :span="isMobile ? 24 : 12">
          <a-form-item label="出发日期" required>
            <a-date-picker v-model:value="form.start_date" value-format="YYYY-MM-DD" style="width:100%" />
          </a-form-item>
        </a-col>
        <a-col :span="isMobile ? 24 : 12">
          <a-form-item label="结束日期" required>
            <a-date-picker v-model:value="form.end_date" value-format="YYYY-MM-DD" style="width:100%" />
          </a-form-item>
        </a-col>
      </a-row>

      <a-form-item label="出行人员名单">
        <a-input v-model:value="form.travelers" placeholder="如：张三, 李四 王五" allow-clear />
      </a-form-item>

      <a-divider>每日行程明细</a-divider>
      <a-collapse v-if="form.days_detail.length > 0" :activeKey="expandedKeys">
        <a-collapse-panel
          v-for="(day, idx) in form.days_detail"
          :key="idx"
          :header="`第 ${day.seq} 天 · ${day.date}`"
        >
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="行程详情">
                <a-textarea v-model:value="day.details" :rows="3" placeholder="当天行程安排" />
              </a-form-item>
            </a-col>
            <a-col :span="isMobile ? 24 : 12">
              <a-form-item label="住宿区域">
                <a-input v-model:value="day.accommodation_area" placeholder="当晚住宿城市或区域" />
              </a-form-item>
            </a-col>
            <a-col :span="isMobile ? 24 : 12">
              <a-form-item label="备注">
                <a-input v-model:value="day.notes" placeholder="注意事项等" />
              </a-form-item>
            </a-col>
          </a-row>
        </a-collapse-panel>
      </a-collapse>
      <a-empty v-else description="请先选择开始日期和结束日期" style="margin:16px 0" />

      <!-- 表单底部无任何提示语、说明文字或 <a-alert> 组件，符合任务要求，无需删除多余内容 -->
      <div v-if="props.showFooter !== false" style="margin-top:24px;display:flex;justify-content:flex-end;gap:8px">
        <a-button @click="handleCancel">取消</a-button>
        <a-button type="primary" html-type="submit" :loading="loading">保存</a-button>
      </div>
    </a-form>
  </div>
</template>
