<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { message } from 'ant-design-vue'
import { FilterOutlined } from '@ant-design/icons-vue'
import { orderApi } from '@/api/order'
import { productApi } from '@/api/product'
import { supplierApi } from '@/api/supplier'
import type { Order, OrderCreate } from '@/types'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const items = ref<Order[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ keyword: '', product_id: undefined as number | undefined, supplier_id: undefined as number | undefined, status: undefined as string | undefined, page: 1, page_size: 20 })

const STATUS_LABEL: Record<string, string> = { pending_deposit: '待下架', pending_payment: '待付款', completed: '已完成' }
const STATUS_COLOR: Record<string, string> = { pending_deposit: 'default', pending_payment: 'processing', completed: 'success' }
const statusOptions = [
  { label: '待下架', value: 'pending_deposit' },
  { label: '待付款', value: 'pending_payment' },
  { label: '已完成', value: 'completed' },
]

const products = ref<{ id: number; name: string; days: number }[]>([])
const suppliers = ref<{ id: number; name: string }[]>([])

const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<OrderCreate>>({ status: 'pending_deposit' })

const drawerViewOpen = ref(false)
const drawerViewData = ref<Order | null>(null)
const drawerLoading = ref(false)

const updateBalanceAmount = () => {
  if (form.value.price != null && form.value.deposit != null) {
    form.value.balance_amount = form.value.price - form.value.deposit
  }
}

const onDepositDueDateChange = (value: string) => {
  if (!value) {
    form.value.deposit_due_date = new Date().toISOString().split('T')[0]
  }
}

const balanceAmountPlaceholder = computed(() => {
  if (form.value.price != null && form.value.deposit != null) {
    return `默认 ${form.value.price - form.value.deposit}`
  }
  return '价格 - 定金'
})

const balanceDueDatePlaceholder = computed(() => {
  if (form.value.travel_date && form.value.days) {
    const date = new Date(form.value.travel_date)
    date.setDate(date.getDate() + form.value.days - 1)
    return date.toISOString().split('T')[0]
  }
  return '行程结束日期'
})

const columns = [
  { title: '', key: '_seq', width: 50, align: 'center' as const },
  { title: '订单编号', dataIndex: 'order_no', width: 160, ellipsis: true },
  { title: '产品', dataIndex: 'product_name', width: 150, ellipsis: true },
  { title: '客户姓名', dataIndex: 'customer_name', width: 80 },
  { title: '手机号', dataIndex: 'customer_phone', width: 120 },
  { title: '出行日期', dataIndex: 'travel_date', width: 100 },
  { title: '供应商', dataIndex: 'supplier_name', width: 120, ellipsis: true },
  { title: '价格(元)', dataIndex: 'price', width: 90, align: 'right', customRender: ({ text }: any) => text != null ? `¥${text.toLocaleString()}` : '-' },
  { title: '状态', key: 'status', width: 85 },
  { title: '操作', key: 'action', width: 130, fixed: 'right' as const },
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
  products.value = (pr.data?.items ?? pr.data ?? []).map((p: any) => ({ id: p.id, name: p.name, days: p.days }))
  suppliers.value = (sr.data?.items ?? sr.data ?? []).map((s: any) => ({ id: s.id, name: s.name }))
}

function openCreate() {
  editingId.value = null
  form.value = { status: 'pending_deposit' }
  drawerOpen.value = true
}

async function openEdit(record: Order) {
  editingId.value = record.id
  form.value = {
    ...record,
    product_id: record.product_id ?? undefined,
    supplier_id: record.supplier_id ?? undefined,
    cost: record.cost ?? undefined,
    deposit: record.deposit ?? undefined,
  }
  drawerOpen.value = true
}

function onProductChange(productId: number) {
  const p = products.value.find(x => x.id === productId)
  if (p) {
    if (p.days) form.value.days = p.days
  }
}

function onSupplierChange(supplierId: number) {
  // 不再需要设置 supplier_name
}

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerViewData.value = null
  drawerLoading.value = true
  try {
    const res = await orderApi.get(id)
    drawerViewData.value = res.data
  } catch {
    message.error('加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function save() {
  if (!form.value.product_id) { message.error('请选择产品'); return }
  if (!form.value.supplier_id) { message.error('请选择供应商'); return }
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
const mobileFilterOpen = ref(false)
const mobileFilter = reactive({ keyword: '', product_id: undefined as number | undefined, supplier_id: undefined as number | undefined, status: undefined as string | undefined })

const activeFilterCount = computed(() => {
  let n = 0
  if (query.keyword) n++
  if (query.product_id != null) n++
  if (query.supplier_id != null) n++
  if (query.status != null) n++
  return n
})

function openMobileFilter() {
  mobileFilter.keyword = query.keyword
  mobileFilter.product_id = query.product_id
  mobileFilter.supplier_id = query.supplier_id
  mobileFilter.status = query.status
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  query.keyword = mobileFilter.keyword
  query.product_id = mobileFilter.product_id
  query.supplier_id = mobileFilter.supplier_id
  query.status = mobileFilter.status
  query.page = 1
  mobileFilterOpen.value = false
  fetchList()
}

function resetMobileFilter() {
  mobileFilter.keyword = ''
  mobileFilter.product_id = undefined
  mobileFilter.supplier_id = undefined
  mobileFilter.status = undefined
}
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <!-- 桌面端筛选表单?-->
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="关键词">
          <a-input v-model:value="query.keyword" placeholder="客户姓名/手机号/订单号" allow-clear style="width:200px"
            @change="() => { query.page = 1; fetchList() }" @pressEnter="() => { query.page = 1; fetchList() }" />
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
          <a-button @click="() => { query.keyword = ''; query.product_id = undefined; query.supplier_id = undefined; query.status = undefined; query.page = 1; fetchList() }">重置</a-button>
        </a-form-item>
      </a-form>
      <!-- 移动端筛选按钮?-->
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter">
          <template #icon><filter-outlined /></template>
          筛选        </a-button>
      </a-badge>
      <a-button type="primary" @click="openCreate">新增订单</a-button>
    </div>

    <!-- 移动端卡片列表?-->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="items" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;color:#111827;font-size:14px">{{ record.order_no }}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">{{ record.customer_name }} · {{ record.product_name }}</div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:2px">出行：{{ record.travel_date ?? '-' }}</div>
                  </div>
                  <a-tag :color="STATUS_COLOR[record.status]" style="margin:0">{{ STATUS_LABEL[record.status] }}</a-tag>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:8px">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button size="small" :disabled="record.status === 'completed'" @click="record.status !== 'completed' && openEdit(record)">编辑</a-button>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
        <div style="display:flex;justify-content:center;margin-top:12px">
          <a-pagination
            :total="total"
            :current="query.page"
            :page-size="query.page_size"
            size="small"
            :show-size-changer="false"
            @change="(p: number) => { query.page = p; fetchList() }"
          />
        </div>
      </a-spin>
    </template>

    <!-- 桌面端表格?-->
    <a-table v-else :columns="columns" :data-source="items" :loading="loading" row-key="id"
      :scroll="{ x: 1050 }"
      :pagination="{ total, current: query.page, pageSize: query.page_size, showTotal: (t: number) => `共 ${t} 条`, onChange: (p: number) => { query.page = p; fetchList() } }"
      size="middle">
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ (query.page - 1) * query.page_size + index + 1 }}</template>
        <template v-else-if="column.key === 'status'">
          <a-tag :color="STATUS_COLOR[record.status]">{{ STATUS_LABEL[record.status] }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button size="small" :disabled="record.status === 'completed'" @click="record.status !== 'completed' && openEdit(record)">编辑</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉?-->
    <a-drawer
      v-if="isMobile"
      title="筛选"
      placement="bottom"
      height="60vh"
      :open="mobileFilterOpen"
      @close="mobileFilterOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="关键词">
          <a-input v-model:value="mobileFilter.keyword" placeholder="客户姓名/手机号/订单号" allow-clear />
        </a-form-item>
        <a-form-item label="产品">
          <a-select v-model:value="mobileFilter.product_id" placeholder="全部" allow-clear style="width:100%">
            <a-select-option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="供应商">
          <a-select v-model:value="mobileFilter.supplier_id" placeholder="全部" allow-clear style="width:100%">
            <a-select-option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="mobileFilter.status" placeholder="全部" allow-clear style="width:100%" :options="statusOptions" />
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
      title="订单详情"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : 560"
      placement="right"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerViewData">
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="订单编号">{{ drawerViewData.order_no }}</a-descriptions-item>
            <a-descriptions-item label="客户姓名">{{ drawerViewData.customer_name }}</a-descriptions-item>
            <a-descriptions-item label="手机号">{{ drawerViewData.customer_phone }}</a-descriptions-item>
            <a-descriptions-item label="产品">{{ drawerViewData.product_name ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="出行日期">{{ drawerViewData.travel_date }}</a-descriptions-item>
            <a-descriptions-item label="天数">{{ drawerViewData.days }} 天</a-descriptions-item>
            <a-descriptions-item label="人数">{{ drawerViewData.people_count }} 人</a-descriptions-item>
            <a-descriptions-item label="价格">
              ¥{{ drawerViewData.price?.toLocaleString() ?? '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="定金">
              {{ drawerViewData.deposit != null ? `¥${drawerViewData.deposit.toLocaleString()}` : '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="供应商">{{ drawerViewData.supplier_name ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="定金到账日期">{{ drawerViewData.deposit_due_date ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="尾款金额">{{ drawerViewData.balance_amount != null ? `¥${drawerViewData.balance_amount.toLocaleString()}` : '-' }}</a-descriptions-item>
            <a-descriptions-item label="尾款到账日期">{{ drawerViewData.balance_due_date ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="成本">
              {{ drawerViewData.cost != null ? `¥${drawerViewData.cost.toLocaleString()}` : '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="利润">
              {{ drawerViewData.profit != null ? `¥${drawerViewData.profit.toLocaleString()}` : '-' }}
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="STATUS_COLOR[drawerViewData.status]">{{ STATUS_LABEL[drawerViewData.status] }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="备注">{{ drawerViewData.remarks ?? '-' }}</a-descriptions-item>
          </a-descriptions>
        </template>
      </a-spin>
    </a-drawer>

    <!-- 表单抽屉 -->
    <a-drawer
      :title="editingId ? '编辑订单' : '新增订单'"
      :open="drawerOpen"
      :width="isMobile ? '100%' : 560"
      placement="right"
      @close="drawerOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="产品" required>
          <a-select v-model:value="form.product_id" placeholder="请选择产品" allow-clear style="width:100%" @change="onProductChange">
            <a-select-option v-for="p in products" :key="p.id" :value="p.id">{{ p.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="客户姓名" required>
              <a-input v-model:value="form.customer_name" placeholder="请输入客户姓名" />
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="手机号" required>
              <a-input v-model:value="form.customer_phone" placeholder="请输入手机号" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="出行日期" required>
              <a-date-picker v-model:value="form.travel_date" value-format="YYYY-MM-DD" style="width:100%" />
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="人数" required>
              <a-input-number v-model:value="form.people_count" :min="1" style="width:100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="天数">
              <a-input-number v-model:value="form.days" :min="1" style="width:100%" />
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="销售价格(元)" required>
              <a-input-number v-model:value="form.price" :min="0" :precision="0" style="width:100%" @change="updateBalanceAmount" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="供应商" required>
              <a-select v-model:value="form.supplier_id" placeholder="请选择供应商" allow-clear style="width:100%" @change="onSupplierChange">
                <a-select-option v-for="s in suppliers" :key="s.id" :value="s.id">{{ s.name }}</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="成本(元)">
              <a-input-number v-model:value="form.cost" :min="0" :precision="0" style="width:100%" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="定金(元)">
              <a-input-number v-model:value="form.deposit" :min="0" :precision="0" style="width:100%" @change="updateBalanceAmount" />
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="定金到账日期">
              <a-date-picker v-model:value="form.deposit_due_date" value-format="YYYY-MM-DD" style="width:100%" @change="onDepositDueDateChange" />
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="尾款(元)">
              <a-input-number v-model:value="form.balance_amount" :min="0" :precision="0" style="width:100%" :placeholder="balanceAmountPlaceholder" />
            </a-form-item>
          </a-col>
          <a-col :span="isMobile ? 24 : 12">
            <a-form-item label="尾款到账日期">
              <a-date-picker v-model:value="form.balance_due_date" value-format="YYYY-MM-DD" style="width:100%" :placeholder="balanceDueDatePlaceholder" />
            </a-form-item>
          </a-col>
        </a-row>
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
