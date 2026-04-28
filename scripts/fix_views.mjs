import { writeFileSync } from 'fs'
import { join } from 'path'

const src = 'e:/Code/TourMind/frontend/src'

// ── ContractListView.vue ──────────────────────────────────────────
writeFileSync(join(src, 'views/contract/ContractListView.vue'), `<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import { contractApi } from '@/api/contract'
import type { ContractListItem } from '@/types'

const router = useRouter()
const items = ref<ContractListItem[]>([])
const loading = ref(false)
const filterStatus = ref<string | undefined>()

const drawerOpen = ref(false)
const windowWidth = ref(window.innerWidth)
window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })

const STATUS_COLOR: Record<string, string> = {
  pending_sign: 'orange', completed: 'success',
}
const STATUS_LABEL: Record<string, string> = {
  pending_sign: '待签署', completed: '已完成',
}

const columns = [
  { title: '合同编号', dataIndex: 'contract_no', width: 180 },
  { title: '关联订单', dataIndex: 'order_no', width: 180 },
  { title: '客户', dataIndex: 'customer_name', width: 100 },
  { title: '状态', key: 'status', width: 100 },
  { title: '创建时间', dataIndex: 'created_at', width: 160, customRender: ({ text }: any) => text?.slice(0, 16).replace('T', ' ') },
  { title: '操作', key: 'action', width: 160 },
]

async function load() {
  loading.value = true
  try {
    const res = await contractApi.list({ status: filterStatus.value })
    items.value = res.data?.items ?? res.data ?? []
  } finally {
    loading.value = false
  }
}

function doDelete(id: number) {
  Modal.confirm({
    title: '确认删除此合同？',
    okType: 'danger',
    onOk: async () => { await contractApi.delete(id); message.success('已删除'); load() },
  })
}

onMounted(load)
</script>

<template>
  <div style="padding:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form layout="inline">
        <a-form-item label="状态">
          <a-select v-model:value="filterStatus" placeholder="全部" allow-clear style="width:120px" @change="load">
            <a-select-option v-for="(label, key) in STATUS_LABEL" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="load">搜索</a-button>
        </a-form-item>
      </a-form>
      <a-button type="primary" @click="drawerOpen = true">新建合同</a-button>
    </div>

    <a-table :columns="columns" :data-source="items" :loading="loading" :scroll="{ x: 800 }" row-key="id" size="small">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="STATUS_COLOR[record.status] ?? 'default'">{{ STATUS_LABEL[record.status] ?? record.status }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="router.push(\`/contracts/\${record.id}\`)">详情</a-button>
            <a-button v-if="record.status === 'pending_sign'" size="small" danger @click="doDelete(record.id)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 新建合同抽屉 -->
    <a-drawer
      title="新建合同"
      :open="drawerOpen"
      :width="Math.min(520, windowWidth)"
      placement="right"
      :destroy-on-close="true"
      @close="drawerOpen = false"
    >
      <ContractCreateForm @saved="(id) => { drawerOpen = false; router.push(\`/contracts/\${id}\`) }" @cancel="drawerOpen = false" />
    </a-drawer>
  </div>
</template>
`, 'utf8')
console.log('ContractListView.vue written')

// ── ContractFormView.vue (renamed to focus: create contract from order) ──
writeFileSync(join(src, 'views/contract/ContractFormView.vue'), `<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { contractApi } from '@/api/contract'
import { orderApi } from '@/api/order'

const emit = defineEmits<{ saved: [id: number]; cancel: [] }>()

const loading = ref(false)
const orderId = ref<number | undefined>()
const orderOptions = ref<{ id: number; label: string }[]>([])

onMounted(async () => {
  const res = await orderApi.list({ page_size: 100 })
  orderOptions.value = (res.data?.items ?? res.data ?? [])
    .filter((o: any) => o.status !== 'completed')
    .map((o: any) => ({ id: o.id, label: \`\${o.order_no} · \${o.customer_name} · \${o.product_name ?? ''}\` }))
})

async function save() {
  if (!orderId.value) { message.error('请选择关联订单'); return }
  loading.value = true
  try {
    const res = await contractApi.create({ order_id: orderId.value })
    message.success('合同已创建')
    emit('saved', res.data.id)
  } finally {
    loading.value = false
  }
}

defineExpose({ resetForm: () => { orderId.value = undefined } })
</script>

<template>
  <a-form layout="vertical">
    <a-form-item label="关联订单" required>
      <a-select v-model:value="orderId" placeholder="请选择订单" style="width:100%" show-search
        filter-option
        :filter-option="(input: string, opt: any) => opt.label?.toLowerCase().includes(input.toLowerCase())">
        <a-select-option v-for="o in orderOptions" :key="o.id" :value="o.id" :label="o.label">
          {{ o.label }}
        </a-select-option>
      </a-select>
    </a-form-item>
    <a-alert type="info" message="创建合同后可在详情页生成分享链接发给客户签署" show-icon style="margin-bottom:16px" />
  </a-form>
  <div style="margin-top:24px">
    <a-space>
      <a-button @click="emit('cancel')">取消</a-button>
      <a-button type="primary" :loading="loading" @click="save">创建合同</a-button>
    </a-space>
  </div>
</template>
`, 'utf8')
console.log('ContractFormView.vue written')

// ── ItineraryFormView.vue ─────────────────────────────────────────
writeFileSync(join(src, 'views/itinerary/ItineraryFormView.vue'), `<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { MinusCircleOutlined, PlusOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import { itineraryApi } from '@/api/itinerary'
import { orderApi } from '@/api/order'
import type { Traveler } from '@/types'

const props = defineProps<{ editId?: number | null }>()
const emit = defineEmits<{ saved: [id: number]; cancel: [] }>()

const router = useRouter()
const route = useRoute()
const routeId = computed(() => route.params.id ? Number(route.params.id) : null)
const resolvedId = computed(() => props.editId ?? routeId.value)
const isEdit = computed(() => !!resolvedId.value)

const loading = ref(false)
const orderOptions = ref<{ id: number; order_no: string; customer_name: string; product_name: string; travel_date: string }[]>([])

interface DayDetail {
  seq: number
  date: string
  details: string
  accommodation_area: string
  notes: string
}

const form = reactive({
  order_id: undefined as number | undefined,
  destination: '',
  pax: 1,
  travelers: [] as Traveler[],
  start_date: '',
  end_date: '',
  status: 'active',
  days_detail: [] as DayDetail[],
})

function resetForm() {
  Object.assign(form, {
    order_id: undefined, destination: '', pax: 1,
    travelers: [], start_date: '', end_date: '', status: 'active', days_detail: [],
  })
}

async function loadOrders() {
  const res = await orderApi.list({ page_size: 100 })
  orderOptions.value = (res.data?.items ?? res.data ?? []).map((o: any) => ({
    id: o.id,
    order_no: o.order_no,
    customer_name: o.customer_name,
    product_name: o.product_name ?? '',
    travel_date: o.travel_date,
  }))
}

function onOrderChange(orderId: number) {
  const o = orderOptions.value.find(x => x.id === orderId)
  if (!o) return
  form.start_date = o.travel_date
  // auto-fill destination from order product if available
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

async function load() {
  const res = await itineraryApi.get(resolvedId.value!)
  const d = res.data
  form.order_id = d.order_id ?? undefined
  form.destination = d.destination ?? ''
  form.pax = d.pax ?? 1
  form.travelers = d.travelers ?? []
  form.start_date = d.start_date ?? ''
  form.end_date = d.end_date ?? ''
  form.status = d.status ?? 'active'
  form.days_detail = (d.days_detail ?? []).map((x: any, i: number) => ({
    seq: x.seq ?? i + 1,
    date: x.date ?? '',
    details: x.details ?? '',
    accommodation_area: x.accommodation_area ?? '',
    notes: x.notes ?? '',
  }))
}

async function handleSubmit() {
  if (!form.order_id) { message.error('请选择关联订单'); return }
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
      if (!props.editId) router.push(\`/itineraries/\${res.data.id}\`)
    }
  } finally {
    loading.value = false
  }
}

function handleCancel() {
  emit('cancel')
  if (!props.editId) router.back()
}

function addTraveler() { form.travelers.push({ name: '' }) }
function removeTraveler(i: number) { form.travelers.splice(i, 1) }

onMounted(() => {
  loadOrders()
  if (isEdit.value) load()
  else resetForm()
})

watch(() => props.editId, (val) => {
  resetForm()
  if (val) load()
})

defineExpose({ resetForm })
</script>

<template>
  <div>
    <a-form layout="vertical" @finish="handleSubmit">
      <!-- 关联订单 -->
      <a-form-item label="关联订单" required>
        <a-select
          v-model:value="form.order_id"
          placeholder="请选择关联订单"
          style="width:100%"
          show-search
          :filter-option="(input: string, opt: any) => opt.label?.toLowerCase().includes(input.toLowerCase())"
          @change="onOrderChange"
        >
          <a-select-option
            v-for="o in orderOptions" :key="o.id" :value="o.id"
            :label="\`\${o.order_no} \${o.customer_name}\`"
          >
            <div>{{ o.order_no }} · {{ o.customer_name }}</div>
            <div style="font-size:12px;color:#8c8c8c">{{ o.product_name }}  {{ o.travel_date }}</div>
          </a-select-option>
        </a-select>
      </a-form-item>

      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item label="目的地" required>
            <a-input v-model:value="form.destination" placeholder="如：桂林" />
          </a-form-item>
        </a-col>
        <a-col :span="6">
          <a-form-item label="出发日期" required>
            <a-date-picker v-model:value="form.start_date" value-format="YYYY-MM-DD" style="width:100%" />
          </a-form-item>
        </a-col>
        <a-col :span="6">
          <a-form-item label="结束日期" required>
            <a-date-picker v-model:value="form.end_date" value-format="YYYY-MM-DD" style="width:100%" />
          </a-form-item>
        </a-col>
        <a-col :span="6">
          <a-form-item label="出行人数" required>
            <a-input-number v-model:value="form.pax" :min="1" style="width:100%" />
          </a-form-item>
        </a-col>
      </a-row>

      <a-form-item label="出行人员名单">
        <div v-for="(t, i) in form.travelers" :key="i" style="display:flex;gap:8px;margin-bottom:8px">
          <a-input v-model:value="t.name" placeholder="姓名" style="width:160px" />
          <a-input v-model:value="t.id_no" placeholder="证件号（选填）" style="width:200px" />
          <MinusCircleOutlined style="color:red;cursor:pointer;margin-top:6px" @click="removeTraveler(i)" />
        </div>
        <a-button type="dashed" @click="addTraveler"><PlusOutlined /> 添加人员</a-button>
      </a-form-item>

      <a-divider>每日行程明细</a-divider>
      <a-collapse v-if="form.days_detail.length > 0">
        <a-collapse-panel
          v-for="(day, idx) in form.days_detail"
          :key="idx"
          :header="\`第 \${day.seq} 天 · \${day.date}\`"
        >
          <a-row :gutter="16">
            <a-col :span="24">
              <a-form-item label="行程详情">
                <a-textarea v-model:value="day.details" :rows="3" placeholder="当天行程安排" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="住宿区域">
                <a-input v-model:value="day.accommodation_area" placeholder="当晚住宿城市或区域" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="备注">
                <a-input v-model:value="day.notes" placeholder="注意事项等" />
              </a-form-item>
            </a-col>
          </a-row>
        </a-collapse-panel>
      </a-collapse>
      <a-empty v-else description="请先选择开始日期和结束日期" style="margin:16px 0" />

      <div style="margin-top:24px">
        <a-button type="primary" html-type="submit" :loading="loading">保存</a-button>
        <a-button style="margin-left:8px" @click="handleCancel">取消</a-button>
      </div>
    </a-form>
  </div>
</template>
`, 'utf8')
console.log('ItineraryFormView.vue written')

// ── BillListView.vue ──────────────────────────────────────────────
// Fix: INCOME_TYPES, EXPENSE_TYPES, null→undefined in openEdit
const billContent = `<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
const windowWidth = ref(window.innerWidth)
window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })
import { billApi } from '@/api/bill'
import { supplierApi } from '@/api/supplier'
import { accountApi } from '@/api/account'
import type { Bill, Supplier, Account } from '@/types'

const bills = ref<Bill[]>([])
const suppliers = ref<Supplier[]>([])
const accounts = ref<Account[]>([])
const total = ref(0)
const loading = ref(false)

const query = reactive({ bill_type: undefined as string | undefined, page: 1, page_size: 20 })
const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<any>({ bill_type: 'income', amount: undefined, bill_date: undefined, account_id: undefined })

onMounted(async () => {
  const [sRes, aRes] = await Promise.all([supplierApi.list({ page_size: 200 }), accountApi.list({ page_size: 200 })])
  suppliers.value = sRes.data?.items ?? sRes.data ?? []
  accounts.value = aRes.data?.items ?? aRes.data ?? []
  fetchBills()
})

async function fetchBills() {
  loading.value = true
  const res = await billApi.list(query)
  bills.value = res.data?.items ?? res.data ?? []
  total.value = res.data?.total ?? bills.value.length
  loading.value = false
}

function openCreate() {
  editingId.value = null
  form.value = { bill_type: 'income', amount: undefined, bill_date: undefined, account_id: undefined, income_type: undefined, expense_type: undefined, supplier_id: undefined, notes: undefined }
  drawerOpen.value = true
}

function openEdit(b: Bill) {
  editingId.value = b.id
  // Convert null → undefined so AntD components don't crash
  form.value = {
    ...b,
    income_type: b.income_type ?? undefined,
    expense_type: b.expense_type ?? undefined,
    supplier_id: (b as any).supplier_id ?? undefined,
    account_id: b.account_id ?? undefined,
    bill_date: b.bill_date ?? undefined,
    notes: (b as any).notes ?? undefined,
  }
  drawerOpen.value = true
}

async function save() {
  if (!form.value.amount) { message.error('请输入金额'); return }
  if (!form.value.bill_date) { message.error('请选择日期'); return }
  if (editingId.value) {
    await billApi.update(editingId.value, form.value)
  } else {
    await billApi.create(form.value)
  }
  drawerOpen.value = false
  message.success('保存成功')
  fetchBills()
}

async function remove(id: number) {
  Modal.confirm({
    title: '确认删除？',
    onOk: async () => { await billApi.delete(id); fetchBills() },
  })
}

const INCOME_TYPES = ['定金', '尾款', '全款', '其他']
const EXPENSE_TYPES = ['供应商付款', '运营成本', '其他']

const columns = [
  { title: '类型', dataIndex: 'bill_type', width: 70, customRender: ({ text }: any) => text === 'income' ? '收入' : '支出' },
  { title: '金额', dataIndex: 'amount', width: 110, align: 'right' as const,
    customRender: ({ text, record }: any) => (record.bill_type === 'income' ? '+' : '-') + '¥' + Number(text).toLocaleString() },
  { title: '收支类目', key: 'category', width: 110, customRender: ({ record }: any) => record.income_type ?? record.expense_type ?? '—' },
  { title: '关联订单', dataIndex: 'order_no', width: 170, customRender: ({ text }: any) => text ?? '—' },
  { title: '账户', dataIndex: 'account_name', width: 150, customRender: ({ text }: any) => text ?? '—' },
  { title: '日期', dataIndex: 'bill_date', width: 110 },
  { title: '备注', dataIndex: 'notes', ellipsis: true, customRender: ({ text }: any) => text ?? '' },
  { title: '操作', key: 'action', width: 110 },
]
<\/script>

<template>
  <div style="padding:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form layout="inline">
        <a-form-item label="收支类型">
          <a-select v-model:value="query.bill_type" placeholder="全部" style="width:120px" allow-clear @change="fetchBills">
            <a-select-option value="income">收入</a-select-option>
            <a-select-option value="expense">支出</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="fetchBills">查询</a-button>
        </a-form-item>
      </a-form>
      <a-button type="primary" @click="openCreate">录入账单</a-button>
    </div>

    <a-table
      :data-source="bills"
      :columns="columns"
      :loading="loading"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchBills() } }"
      :scroll="{ x: 900 }"
      row-key="id"
      size="small"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
            <a-button size="small" danger @click="remove(record.id)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-drawer
      :title="editingId ? '编辑账单' : '录入账单'"
      :open="drawerOpen"
      :width="Math.min(480, windowWidth)"
      placement="right"
      @close="drawerOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="收支类型">
          <a-radio-group v-model:value="form.bill_type">
            <a-radio-button value="income">收入</a-radio-button>
            <a-radio-button value="expense">支出</a-radio-button>
          </a-radio-group>
        </a-form-item>
        <a-form-item v-if="form.bill_type === 'income'" label="收入类目">
          <a-select v-model:value="form.income_type" placeholder="请选择" allow-clear style="width:100%">
            <a-select-option v-for="t in INCOME_TYPES" :key="t" :value="t">{{ t }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item v-else label="支出类目">
          <a-select v-model:value="form.expense_type" placeholder="请选择" allow-clear style="width:100%">
            <a-select-option v-for="t in EXPENSE_TYPES" :key="t" :value="t">{{ t }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="金额（元）" required>
          <a-input-number v-model:value="form.amount" :min="0" :precision="2" prefix="¥" style="width:100%" />
        </a-form-item>
        <a-form-item label="账单日期" required>
          <a-date-picker v-model:value="form.bill_date" value-format="YYYY-MM-DD" style="width:100%" />
        </a-form-item>
        <a-form-item label="收款/付款账户">
          <a-select v-model:value="form.account_id" placeholder="请选择账户" allow-clear style="width:100%">
            <a-select-option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item v-if="form.bill_type === 'expense'" label="供应商（可选）">
          <a-select v-model:value="form.supplier_id" allow-clear placeholder="请选择供应商" style="width:100%">
            <a-select-option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea v-model:value="form.notes" :rows="2" />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="drawerOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
`
writeFileSync(join(src, 'views/bill/BillListView.vue'), billContent, 'utf8')
console.log('BillListView.vue written')

console.log('All views written!')
