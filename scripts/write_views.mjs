import { writeFileSync } from 'fs'
import { join } from 'path'

const root = 'e:/Code/TourMind'
const src = `${root}/frontend/src`

// ─── types/index.ts ───────────────────────────────────────────────
writeFileSync(join(src, 'types/index.ts'), `// ── 用户 ───────────────────────────────────────────────────────────
export interface UserInfo {
  id: number
  name: string
  phone: string | null
  employee_id: string | null
  role: 'system_admin' | 'admin' | 'assistant'
  is_active: boolean
  last_login_at: string | null
  created_at: string
}

// ── 供应商 ─────────────────────────────────────────────────────────
export interface Supplier {
  id: number
  name: string
  contact_person: string | null
  contact_phone: string | null
  notes: string | null
  is_active: boolean
  created_at: string
}

// ── 账户 ───────────────────────────────────────────────────────────
export interface Account {
  id: number
  name: string
  account_type: string
  description: string | null
  user_id: number | null
  user_name: string | null
  notes: string | null
  is_active: boolean
  created_at: string
}

// ── 产品 ───────────────────────────────────────────────────────────
export interface ProductTemplateDay {
  seq: number
  details: string
  accommodation_area?: string | null
  notes?: string | null
}

export interface Product {
  id: number
  name: string
  destination: string
  days: number
  reference_price: number | null
  includes: string | null
  excludes: string | null
  cancellation_policy: string | null
  travel_notice: string | null
  important_tips: string | null
  itinerary_template: ProductTemplateDay[] | null
  notes: string | null
  status: string
  created_at: string
}

export type ProductListItem = Pick<Product, 'id' | 'name' | 'destination' | 'days' | 'reference_price' | 'status' | 'created_at'>
export type ProductCreate = Omit<Product, 'id' | 'created_at'>
export type ProductUpdate = Partial<ProductCreate>

// ── 订单 ───────────────────────────────────────────────────────────
export interface Order {
  id: number
  order_no: string
  product_id: number | null
  product_name: string | null
  customer_name: string
  customer_phone: string
  travel_date: string
  days: number
  price: number
  deposit: number | null
  supplier_id: number | null
  supplier_name: string | null
  cost: number | null
  profit: number | null
  status: 'pending_deposit' | 'pending_payment' | 'completed'
  user_id: number | null
  created_at: string
}

export type OrderListItem = Order
export type OrderCreate = Omit<Order, 'id' | 'order_no' | 'profit' | 'created_at'>
export type OrderUpdate = Partial<OrderCreate>

// ── 行程 ───────────────────────────────────────────────────────────
export interface Traveler {
  name: string
  id_no?: string
}

export interface ItineraryDayDetail {
  seq: number
  details: string
  accommodation_area?: string | null
  notes?: string | null
}

export interface Itinerary {
  id: number
  order_id: number
  order_no: string
  product_name: string | null
  customer_name: string
  customer_phone: string
  destination: string
  pax: number
  travelers: Traveler[] | null
  start_date: string
  end_date: string
  status: string
  days_detail: ItineraryDayDetail[]
  created_at: string
}

export type ItineraryListItem = Pick<Itinerary, 'id' | 'order_id' | 'order_no' | 'customer_name' | 'destination' | 'start_date' | 'end_date' | 'pax' | 'status' | 'created_at'>
export type ItineraryCreate = Omit<Itinerary, 'id' | 'created_at'>
export type ItineraryUpdate = Partial<ItineraryCreate>

// ── 合同 ───────────────────────────────────────────────────────────
export interface Contract {
  id: number
  contract_no: string
  order_id: number
  order_no: string
  customer_name: string
  customer_phone: string
  status: 'pending_sign' | 'completed'
  share_token: string | null
  signature_url: string | null
  signed_at: string | null
  created_at: string
}

export type ContractListItem = Pick<Contract, 'id' | 'contract_no' | 'order_id' | 'order_no' | 'customer_name' | 'status' | 'created_at'>
export type ContractCreate = { order_id: number }
export type ContractUpdate = Partial<ContractCreate>

// ── 账单 ───────────────────────────────────────────────────────────
export interface Bill {
  id: number
  order_id: number
  order_no: string
  bill_type: 'income' | 'expense'
  income_type: string | null
  expense_type: string | null
  amount: number
  account_id: number | null
  account_name: string | null
  bill_date: string
  notes: string | null
  attachment_url: string | null
  created_at: string
}

export type BillCreate = Omit<Bill, 'id' | 'created_at' | 'account_name' | 'order_no'>
export type BillUpdate = Partial<BillCreate>

// ── 看板 ───────────────────────────────────────────────────────────
export interface DashboardSummary {
  month_income: number
  month_expense: number
  month_profit: number
  pending_income: number
}
`, 'utf8')
console.log('types/index.ts written')

// ─── views/order/OrderListView.vue ────────────────────────────────
writeFileSync(join(src, 'views/order/OrderListView.vue'), `<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { orderApi } from '@/api/order'
import { productApi } from '@/api/product'
import { supplierApi } from '@/api/supplier'
import type { Order, OrderCreate } from '@/types'

const windowWidth = ref(window.innerWidth)
window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })

const items = ref<Order[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ keyword: '', product_id: undefined as number | undefined, supplier_id: undefined as number | undefined, status: undefined as string | undefined, page: 1, page_size: 20 })

const STATUS_LABEL: Record<string, string> = { pending_deposit: '待下定', pending_payment: '待付款', completed: '已完成' }
const STATUS_COLOR: Record<string, string> = { pending_deposit: 'default', pending_payment: 'processing', completed: 'success' }
const statusOptions = [
  { label: '待下定', value: 'pending_deposit' },
  { label: '待付款', value: 'pending_payment' },
  { label: '已完成', value: 'completed' },
]

const products = ref<{ id: number; name: string }[]>([])
const suppliers = ref<{ id: number; name: string }[]>([])

const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<OrderCreate>>({ status: 'pending_deposit' })

const columns = [
  { title: '订单编号', dataIndex: 'order_no', width: 180, ellipsis: true },
  { title: '产品', dataIndex: 'product_name', width: 160, ellipsis: true },
  { title: '客户姓名', dataIndex: 'customer_name', width: 90 },
  { title: '手机号', dataIndex: 'customer_phone', width: 130 },
  { title: '出行日期', dataIndex: 'travel_date', width: 110 },
  { title: '供应商', dataIndex: 'supplier_name', width: 140, ellipsis: true },
  { title: '价格(元)', dataIndex: 'price', width: 100, align: 'right', customRender: ({ text }: any) => text != null ? \`¥\${text.toLocaleString()}\` : '-' },
  { title: '利润(元)', dataIndex: 'profit', width: 100, align: 'right', customRender: ({ text }: any) => text != null ? \`¥\${text.toLocaleString()}\` : '-' },
  { title: '状态', key: 'status', width: 90 },
  { title: '操作', key: 'action', width: 150 },
]

onMounted(async () => {
  await Promise.all([fetchList(), loadOptions()])
})

async function fetchList() {
  loading.value = true
  try {
    const res = await orderApi.list(query)
    items.value = res.data?.items ?? res.data ?? []
    total.value = res.data?.total ?? items.value.length
  } finally {
    loading.value = false
  }
}

async function loadOptions() {
  const [pr, sr] = await Promise.all([productApi.list({}), supplierApi.list({})])
  products.value = (pr.data?.items ?? pr.data ?? []).map((p: any) => ({ id: p.id, name: p.name }))
  suppliers.value = (sr.data?.items ?? sr.data ?? []).map((s: any) => ({ id: s.id, name: s.name }))
}

function openCreate() {
  editingId.value = null
  form.value = { status: 'pending_deposit' }
  drawerOpen.value = true
}

async function openEdit(record: Order) {
  editingId.value = record.id
  form.value = { ...record }
  drawerOpen.value = true
}

function onProductChange(productId: number) {
  const p = products.value.find(x => x.id === productId)
  if (p) form.value.product_name = p.name
}

function onSupplierChange(supplierId: number) {
  const s = suppliers.value.find(x => x.id === supplierId)
  if (s) form.value.supplier_name = s.name
}

async function save() {
  if (!form.value.customer_name?.trim()) { message.error('请输入客户姓名'); return }
  if (!form.value.customer_phone?.trim()) { message.error('请输入手机号'); return }
  if (!form.value.travel_date) { message.error('请选择出行日期'); return }
  if (!form.value.price) { message.error('请输入价格'); return }

  if (editingId.value) {
    await orderApi.update(editingId.value, form.value as any)
  } else {
    await orderApi.create(form.value as any)
  }
  drawerOpen.value = false
  message.success('保存成功')
  fetchList()
}

function changeStatus(record: Order, nextStatus: string) {
  const label = STATUS_LABEL[nextStatus]
  Modal.confirm({
    title: \`确认将订单状态改为【\${label}】？\`,
    onOk: async () => {
      await orderApi.updateStatus(record.id, nextStatus)
      message.success(\`已更新为\${label}\`)
      fetchList()
    },
  })
}

function doDelete(id: number) {
  Modal.confirm({
    title: '确认删除此订单？',
    okType: 'danger',
    onOk: async () => { await orderApi.delete(id); message.success('已删除'); fetchList() },
  })
}
</script>

<template>
  <div style="padding:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form layout="inline">
        <a-form-item label="关键词">
          <a-input v-model:value="query.keyword" placeholder="客户姓名/手机号/订单号" allow-clear style="width:200px"
            @change="() => { query.page = 1; fetchList() }" />
        </a-form-item>
        <a-form-item label="产品">
          <a-select v-model:value="query.product_id" placeholder="全部" allow-clear style="width:140px" @change="() => { query.page = 1; fetchList() }">
            <a-select-option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="供应商">
          <a-select v-model:value="query.supplier_id" placeholder="全部" allow-clear style="width:140px" @change="() => { query.page = 1; fetchList() }">
            <a-select-option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="query.status" placeholder="全部" allow-clear style="width:110px" :options="statusOptions" @change="() => { query.page = 1; fetchList() }" />
        </a-form-item>
        <a-form-item>
          <a-button @click="() => { query.page = 1; fetchList() }">查询</a-button>
        </a-form-item>
      </a-form>
      <a-button type="primary" @click="openCreate">新增订单</a-button>
    </div>

    <a-table :columns="columns" :data-source="items" :loading="loading" row-key="id"
      :pagination="{ total, current: query.page, pageSize: query.page_size, showTotal: (t: number) => \`共 \${t} 条\`, onChange: (p: number) => { query.page = p; fetchList() } }"
      :scroll="{ x: 1200 }" size="small">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="STATUS_COLOR[record.status]">{{ STATUS_LABEL[record.status] }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
            <a-dropdown>
              <a-button size="small">变更状态 <down-outlined /></a-button>
              <template #overlay>
                <a-menu>
                  <a-menu-item v-for="opt in statusOptions" :key="opt.value"
                    :disabled="record.status === opt.value"
                    @click="changeStatus(record, opt.value)">{{ opt.label }}</a-menu-item>
                </a-menu>
              </template>
            </a-dropdown>
            <a-button size="small" danger @click="doDelete(record.id)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 表单抽屉 -->
    <a-drawer
      :title="editingId ? '编辑订单' : '新增订单'"
      :open="drawerOpen"
      :width="Math.min(560, windowWidth)"
      placement="right"
      @close="drawerOpen = false"
    >
      <a-form layout="vertical">
        <a-row :gutter="12">
          <a-col :span="12">
            <a-form-item label="客户姓名" required>
              <a-input v-model:value="form.customer_name" placeholder="请输入客户姓名" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="手机号" required>
              <a-input v-model:value="form.customer_phone" placeholder="请输入手机号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="12">
            <a-form-item label="产品">
              <a-select v-model:value="form.product_id" placeholder="请选择产品" allow-clear style="width:100%" @change="onProductChange">
                <a-select-option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="供应商">
              <a-select v-model:value="form.supplier_id" placeholder="请选择供应商" allow-clear style="width:100%" @change="onSupplierChange">
                <a-select-option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="12">
            <a-form-item label="出行日期" required>
              <a-date-picker v-model:value="form.travel_date" value-format="YYYY-MM-DD" style="width:100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="天数">
              <a-input-number v-model:value="form.days" :min="1" style="width:100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="8">
            <a-form-item label="销售价格(元)" required>
              <a-input-number v-model:value="form.price" :min="0" :precision="0" style="width:100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="定金(元)">
              <a-input-number v-model:value="form.deposit" :min="0" :precision="0" style="width:100%" />
            </a-form-item>
          </a-col>
          <a-col :span="8">
            <a-form-item label="成本(元)">
              <a-input-number v-model:value="form.cost" :min="0" :precision="0" style="width:100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-form-item label="状态">
          <a-select v-model:value="form.status" style="width:100%" :options="statusOptions" />
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
`, 'utf8')
console.log('OrderListView.vue written')

// ─── views/supplier/SupplierListView.vue ──────────────────────────
writeFileSync(join(src, 'views/supplier/SupplierListView.vue'), `<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
const windowWidth = ref(window.innerWidth)
window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })
import { supplierApi } from '@/api/supplier'
import type { Supplier } from '@/types'

const suppliers = ref<Supplier[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ keyword: '', is_active: undefined as boolean | undefined, page: 1, page_size: 20 })
const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<Supplier>>({ is_active: true })

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await supplierApi.list(query)
  suppliers.value = res.data?.items ?? res.data ?? []
  total.value = res.data?.total ?? suppliers.value.length
  loading.value = false
}

function openCreate() { editingId.value = null; form.value = { is_active: true }; modalOpen.value = true }
function openEdit(s: Supplier) { editingId.value = s.id; form.value = { ...s }; modalOpen.value = true }

async function save() {
  if (!form.value.name?.trim()) { message.error('请输入供应商名称'); return }
  if (editingId.value) {
    await supplierApi.update(editingId.value, form.value)
  } else {
    await supplierApi.create(form.value as any)
  }
  modalOpen.value = false
  message.success('保存成功')
  fetchList()
}

async function remove(id: number) {
  Modal.confirm({ title: '确认删除供应商？', onOk: async () => { await supplierApi.delete(id); fetchList() } })
}

const columns = [
  { title: '名称', dataIndex: 'name', ellipsis: true },
  { title: '联系人', dataIndex: 'contact_person', width: 100 },
  { title: '联系电话', dataIndex: 'contact_phone', width: 140 },
  { title: '备注', dataIndex: 'notes', width: 180, ellipsis: true },
  { title: '状态', key: 'is_active', width: 80, align: 'center' },
  { title: '操作', key: 'action', width: 120 },
]
</script>

<template>
  <div style="padding:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form layout="inline">
        <a-form-item label="名称">
          <a-input v-model:value="query.keyword" placeholder="搜索供应商名称" allow-clear @change="fetchList" style="width:200px" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="query.is_active" placeholder="全部" allow-clear style="width:90px" @change="fetchList">
            <a-select-option :value="true">启用</a-select-option>
            <a-select-option :value="false">停用</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="fetchList">查询</a-button>
        </a-form-item>
      </a-form>
      <a-button type="primary" @click="openCreate">新增供应商</a-button>
    </div>
    <a-table :data-source="suppliers" :columns="columns" :loading="loading"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchList() } }"
      :scroll="{ x: 700 }" row-key="id" size="small">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'default'">{{ record.is_active ? '启用' : '停用' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
            <a-button size="small" danger @click="remove(record.id)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-drawer
      :title="editingId ? '编辑供应商' : '新增供应商'"
      :open="modalOpen"
      :width="Math.min(480, windowWidth)"
      placement="right"
      @close="modalOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="名称" required><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="联系人"><a-input v-model:value="form.contact_person" /></a-form-item>
        <a-form-item label="联系电话"><a-input v-model:value="form.contact_phone" /></a-form-item>
        <a-form-item label="备注"><a-textarea v-model:value="form.notes" :rows="3" /></a-form-item>
        <a-form-item label="状态">
          <a-switch v-model:checked="form.is_active" checked-children="启用" un-checked-children="停用" />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="modalOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
`, 'utf8')
console.log('SupplierListView.vue written')

// ─── views/account/AccountListView.vue ───────────────────────────
writeFileSync(join(src, 'views/account/AccountListView.vue'), `<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
const windowWidth = ref(window.innerWidth)
window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })
import { accountApi } from '@/api/account'
import { userApi } from '@/api/user'
import type { Account } from '@/types'

const accounts = ref<Account[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, page_size: 20 })
const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<Account>>({ account_type: 'bank', is_active: true })

const userOptions = ref<{ id: number; name: string }[]>([])

const TYPES: Record<string, string> = {
  bank: '银行卡', wechat: '微信', alipay: '支付宝', cash: '现金', pos: 'POS机', other: '其他',
}

onMounted(async () => {
  await Promise.all([fetchList(), loadUsers()])
})

async function loadUsers() {
  const res = await userApi.list({ page: 1, page_size: 100 })
  userOptions.value = (res.data?.items ?? res.data ?? []).map((u: any) => ({ id: u.id, name: u.name }))
}

async function fetchList() {
  loading.value = true
  const res = await accountApi.list(query)
  accounts.value = res.data?.items ?? res.data ?? []
  total.value = res.data?.total ?? accounts.value.length
  loading.value = false
}

function openCreate() { editingId.value = null; form.value = { account_type: 'bank', is_active: true }; modalOpen.value = true }
function openEdit(a: Account) { editingId.value = a.id; form.value = { ...a }; modalOpen.value = true }

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

async function remove(id: number) {
  Modal.confirm({ title: '确认删除账户？', onOk: async () => { await accountApi.delete(id); fetchList() } })
}

const columns = [
  { title: '账户名称', dataIndex: 'name', ellipsis: true },
  { title: '类型', dataIndex: 'account_type', width: 90, customRender: ({ text }: any) => TYPES[text] ?? text },
  { title: '描述', dataIndex: 'description', ellipsis: true },
  { title: '负责人', dataIndex: 'user_name', width: 100 },
  { title: '状态', key: 'is_active', width: 80, align: 'center' },
  { title: '操作', key: 'action', width: 120 },
]
</script>

<template>
  <div style="padding:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <span />
      <a-button type="primary" @click="openCreate">新增账户</a-button>
    </div>
    <a-table :data-source="accounts" :columns="columns" :loading="loading"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchList() } }"
      :scroll="{ x: 700 }" row-key="id" size="small">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'default'">{{ record.is_active ? '启用' : '停用' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
            <a-button size="small" danger @click="remove(record.id)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-drawer
      :title="editingId ? '编辑账户' : '新增账户'"
      :open="modalOpen"
      :width="Math.min(480, windowWidth)"
      placement="right"
      @close="modalOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="账户名称" required><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="账户类型">
          <a-select v-model:value="form.account_type" style="width:100%">
            <a-select-option v-for="(label, key) in TYPES" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model:value="form.description" :rows="2" placeholder="账户用途说明" />
        </a-form-item>
        <a-form-item label="负责人">
          <a-select v-model:value="form.user_id" placeholder="请选择负责人" allow-clear style="width:100%" @change="onUserChange">
            <a-select-option v-for="u in userOptions" :key="u.id" :value="u.id">{{ u.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注"><a-textarea v-model:value="form.notes" :rows="2" /></a-form-item>
        <a-form-item label="状态">
          <a-switch v-model:checked="form.is_active" checked-children="启用" un-checked-children="停用" />
        </a-form-item>
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="modalOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
`, 'utf8')
console.log('AccountListView.vue written')

// ─── views/user/UserListView.vue ──────────────────────────────────
writeFileSync(join(src, 'views/user/UserListView.vue'), `<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
const windowWidth = ref(window.innerWidth)
window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })
import { userApi } from '@/api/user'
import type { UserInfo } from '@/types'

const users = ref<UserInfo[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ page: 1, page_size: 20 })
const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<any>({ role: 'assistant', is_active: true })

const ROLES: Record<string, string> = { system_admin: '系统管理员', admin: '管理员', assistant: '助理' }
const ROLE_COLOR: Record<string, string> = { system_admin: 'red', admin: 'blue', assistant: 'green' }

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await userApi.list(query)
  users.value = res.data?.items ?? res.data ?? []
  total.value = res.data?.total ?? users.value.length
  loading.value = false
}

function openCreate() { editingId.value = null; form.value = { role: 'assistant', is_active: true }; modalOpen.value = true }
function openEdit(u: UserInfo) {
  if (u.role === 'system_admin') { message.warning('系统管理员不可编辑'); return }
  editingId.value = u.id; form.value = { ...u }; modalOpen.value = true
}

async function save() {
  if (!form.value.name?.trim()) { message.error('请输入姓名'); return }
  if (!form.value.phone?.trim()) { message.error('请输入手机号'); return }
  if (editingId.value) {
    await userApi.update(editingId.value, form.value)
    message.success('保存成功')
  } else {
    const res = await userApi.create(form.value)
    const pwd = res.data?.generated_password
    if (pwd) {
      Modal.info({ title: '初始密码', content: \`初始密码：\${pwd}，请记录并告知用户\` })
    } else {
      message.success('创建成功')
    }
  }
  modalOpen.value = false
  fetchList()
}

async function resetPwd(u: UserInfo) {
  if (u.role === 'system_admin') { message.warning('系统管理员不可重置密码'); return }
  Modal.confirm({
    title: \`确认重置 \${u.name} 的密码？\`,
    onOk: async () => {
      const res = await userApi.resetPassword(u.id)
      const pwd = res.data?.generated_password
      if (pwd) {
        Modal.info({ title: '新密码', content: \`初始密码：\${pwd}，请告知用户\` })
      }
    },
  })
}

async function remove(u: UserInfo) {
  if (u.role === 'system_admin') { message.warning('系统管理员不可删除'); return }
  Modal.confirm({ title: '确认删除用户？', onOk: async () => { await userApi.remove(u.id); fetchList() } })
}

const columns = [
  { title: '姓名', dataIndex: 'name', width: 100 },
  { title: '手机号', dataIndex: 'phone', width: 140 },
  { title: '工号', dataIndex: 'employee_id', width: 100 },
  { title: '角色', key: 'role', width: 110 },
  { title: '状态', key: 'is_active', width: 80, align: 'center' },
  { title: '最后登录', dataIndex: 'last_login_at', width: 160, customRender: ({ text }: any) => text ? text.slice(0, 16).replace('T', ' ') : '-' },
  { title: '操作', key: 'action', width: 170 },
]
</script>

<template>
  <div style="padding:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <span />
      <a-button type="primary" @click="openCreate">新增用户</a-button>
    </div>
    <a-table :data-source="users" :columns="columns" :loading="loading"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchList() } }"
      :scroll="{ x: 860 }" row-key="id" size="small">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'role'">
          <a-tag :color="ROLE_COLOR[record.role]">{{ ROLES[record.role] ?? record.role }}</a-tag>
        </template>
        <template v-else-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'default'">{{ record.is_active ? '启用' : '禁用' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" :disabled="record.role === 'system_admin'" @click="openEdit(record)">编辑</a-button>
            <a-button size="small" :disabled="record.role === 'system_admin'" @click="resetPwd(record)">重置密码</a-button>
            <a-button size="small" danger :disabled="record.role === 'system_admin'" @click="remove(record)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-drawer
      :title="editingId ? '编辑用户' : '新增用户'"
      :open="modalOpen"
      :width="Math.min(480, windowWidth)"
      placement="right"
      @close="modalOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="姓名" required><a-input v-model:value="form.name" placeholder="请输入姓名" /></a-form-item>
        <a-form-item label="手机号" required><a-input v-model:value="form.phone" placeholder="请输入手机号" /></a-form-item>
        <a-form-item label="工号"><a-input v-model:value="form.employee_id" /></a-form-item>
        <a-form-item label="角色">
          <a-select v-model:value="form.role" style="width:100%">
            <a-select-option v-for="(label, key) in ROLES" :key="key" :value="key">{{ label }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-switch v-model:checked="form.is_active" checked-children="启用" un-checked-children="禁用" />
        </a-form-item>
        <a-alert v-if="!editingId" type="info" message="创建后系统自动生成初始密码" show-icon />
      </a-form>
      <template #footer>
        <a-space>
          <a-button @click="modalOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
`, 'utf8')
console.log('UserListView.vue written')

console.log('All view files written!')
