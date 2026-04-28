<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { message } from 'ant-design-vue'
import { FilterOutlined } from '@ant-design/icons-vue'
const windowWidth = ref(window.innerWidth)
import { billApi } from '@/api/bill'
import { supplierApi } from '@/api/supplier'
import { accountApi } from '@/api/account'
import { orderApi } from '@/api/order'
import type { Bill, Supplier, Account } from '@/types'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const bills = ref<Bill[]>([])
const suppliers = ref<Supplier[]>([])
const accounts = ref<Account[]>([])
const orderOptions = ref<{ id: number; order_no: string; customer_name: string; price: number; status: string; supplier_id: number | undefined; supplier_name: string | undefined }[]>([])
const total = ref(0)
const loading = ref(false)

const query = reactive({
  bill_type: undefined as string | undefined,
  account_id: undefined as number | undefined,
  start_date: undefined as string | undefined,
  end_date: undefined as string | undefined,
  page: 1,
  page_size: 20,
})
const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<any>({ bill_type: 'income', amount: undefined, bill_date: undefined, account_id: undefined })

const drawerViewOpen = ref(false)
const drawerViewData = ref<Bill | null>(null)
const drawerLoading = ref(false)

onMounted(async () => {
  const [sRes, aRes, oRes] = await Promise.all([
    supplierApi.list({ page_size: 200 }),
    accountApi.list({ page_size: 200 }),
    orderApi.list({ page_size: 200 }),
  ])
  suppliers.value = sRes.data?.items ?? sRes.data ?? []
  accounts.value = aRes.data?.items ?? aRes.data ?? []
  const allOrders: any[] = oRes.data?.items ?? oRes.data ?? []
  orderOptions.value = allOrders
    .filter((o: any) => o.status !== 'completed')
    .map((o: any) => ({ id: o.id, order_no: o.order_no, customer_name: o.customer_name, price: o.price, status: o.status, supplier_id: o.supplier_id ?? undefined, supplier_name: o.supplier_name ?? undefined }))
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
  form.value = { bill_type: 'income', amount: undefined, bill_date: undefined, account_id: undefined, income_type: undefined, expense_type: undefined, supplier_id: undefined, notes: undefined, customer_order_id: undefined }
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
    customer_order_id: (b as any).customer_order_id ?? undefined,
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
  if (form.value.bill_type === 'income' && form.value.customer_order_id) {
    await checkAndAdvanceOrderStatus(form.value.customer_order_id)
  }
}

async function checkAndAdvanceOrderStatus(orderId: number) {
  const order = orderOptions.value.find(o => o.id === orderId)
  if (!order) return
  if (order.status === 'pending_deposit') {
    await orderApi.updateStatus(orderId, 'pending_payment')
    message.success('订单状态已自动更新为【待付款】')
  } else if (order.status === 'pending_payment') {
    const res = await billApi.list({ customer_order_id: orderId, bill_type: 'income', page_size: 500 })
    const incomeBills: any[] = res.data?.items ?? res.data ?? []
    const total = incomeBills.reduce((sum: number, b: any) => sum + Number(b.amount ?? 0), 0)
    if (total >= order.price) {
      await orderApi.updateStatus(orderId, 'completed')
      message.success('订单状态已自动更新为【已完成】')
    }
  }
  // Refresh order options so UI reflects latest status
  const oRes = await orderApi.list({ page_size: 200 })
  const allOrders: any[] = oRes.data?.items ?? oRes.data ?? []
  orderOptions.value = allOrders
    .filter((o: any) => o.status !== 'completed')
    .map((o: any) => ({ id: o.id, order_no: o.order_no, customer_name: o.customer_name, price: o.price, status: o.status, supplier_id: o.supplier_id ?? undefined, supplier_name: o.supplier_name ?? undefined }))
}

function onOrderChange(orderId: number | undefined) {
  if (form.value.bill_type === 'expense') {
    if (orderId) {
      const order = orderOptions.value.find(o => o.id === orderId)
      form.value.supplier_id = order?.supplier_id ?? undefined
    } else {
      form.value.supplier_id = undefined
    }
  }
}

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerViewData.value = null
  drawerLoading.value = true
  try {
    const res = await billApi.get(id)
    drawerViewData.value = res.data
  } catch {
    message.error('加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

function onBillTypeChange() {
  form.value.customer_order_id = undefined
  form.value.supplier_id = undefined
}


const mobileFilterOpen = ref(false)
const mobileFilter = reactive({ bill_type: undefined as string | undefined, account_id: undefined as number | undefined, start_date: undefined as string | undefined, end_date: undefined as string | undefined })

const activeFilterCount = computed(() => {
  let n = 0
  if (query.bill_type) n++
  if (query.account_id != null) n++
  if (query.start_date) n++
  return n
})

function openMobileFilter() {
  mobileFilter.bill_type = query.bill_type
  mobileFilter.account_id = query.account_id
  mobileFilter.start_date = query.start_date
  mobileFilter.end_date = query.end_date
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  query.bill_type = mobileFilter.bill_type
  query.account_id = mobileFilter.account_id
  query.start_date = mobileFilter.start_date
  query.end_date = mobileFilter.end_date
  query.page = 1
  mobileFilterOpen.value = false
  fetchBills()
}

function resetMobileFilter() {
  mobileFilter.bill_type = undefined
  mobileFilter.account_id = undefined
  mobileFilter.start_date = undefined
  mobileFilter.end_date = undefined
}

const INCOME_TYPES = ['定金', '尾款', '全款', '其他']
const EXPENSE_TYPES = ['供应商付款', '运营成本', '其他']

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '类型', dataIndex: 'bill_type', width: 70, customRender: ({ text }: any) => text === 'income' ? '收入' : '支出' },
  { title: '金额', dataIndex: 'amount', width: 110, align: 'right' as const,
    customRender: ({ text, record }: any) => (record.bill_type === 'income' ? '+' : '-') + '¥' + Number(text).toLocaleString() },
  { title: '收支类目', key: 'category', width: 110, customRender: ({ record }: any) => record.income_type ?? record.expense_type ?? '—' },
  { title: '关联订单', dataIndex: 'order_no', width: 170, customRender: ({ text }: any) => text ?? '—' },
  { title: '账户', dataIndex: 'account_name', width: 150, customRender: ({ text }: any) => text ?? '—' },
  { title: '日期', dataIndex: 'bill_date', width: 110 },
  { title: '备注', dataIndex: 'notes', width: 150, ellipsis: true, customRender: ({ text }: any) => text ?? '' },
  { title: '操作', key: 'action', width: 130, fixed: 'right' as const },
]
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="收支类型">
          <a-select v-model:value="query.bill_type" placeholder="全部" style="width:120px" allow-clear @change="fetchBills">
            <a-select-option value="income">收入</a-select-option>
            <a-select-option value="expense">支出</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="账户">
          <a-select v-model:value="query.account_id" placeholder="全部账户" style="width:160px" allow-clear @change="fetchBills">
            <a-select-option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="日期范围">
          <a-range-picker
            value-format="YYYY-MM-DD"
            style="width:220px"
            @change="(dates: string[]) => { query.start_date = dates?.[0]; query.end_date = dates?.[1]; fetchBills() }"
          />
        </a-form-item>
        <a-form-item>
          <a-button @click="() => { query.bill_type = undefined; query.account_id = undefined; query.start_date = undefined; query.end_date = undefined; query.page = 1; fetchBills() }">重置</a-button>
        </a-form-item>
      </a-form>
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter"><template #icon><filter-outlined /></template>筛选</a-button>
      </a-badge>
      <a-button type="primary" @click="openCreate">录入账单</a-button>
    </div>

    <!-- 移动端卡片 -->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="bills" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;font-size:14px" :style="{ color: record.bill_type === 'income' ? '#10b981' : '#ef4444' }">
                      {{ record.bill_type === 'income' ? '+' : '-' }}¥{{ Number(record.amount).toLocaleString() }}
                    </div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">{{ record.income_type ?? record.expense_type ?? '—' }}</div>
                    <div v-if="record.order_no" style="font-size:12px;color:#9ca3af;margin-top:2px">订单：{{ record.order_no }}</div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:2px">日期：{{ record.bill_date }}</div>
                  </div>
                  <a-tag :color="record.bill_type === 'income' ? 'green' : 'red'" style="margin:0">{{ record.bill_type === 'income' ? '收入' : '支出' }}</a-tag>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:8px">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button size="small" @click="openEdit(record)">编辑</a-button>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
        <div style="display:flex;justify-content:center;margin-top:12px">
          <a-pagination :total="total" :current="query.page" :page-size="query.page_size" size="small" :show-size-changer="false"
            @change="(p: number) => { query.page = p; fetchBills() }" />
        </div>
      </a-spin>
    </template>

    <!-- 桌面端表格 -->
    <a-table v-else
      :data-source="bills"
      :columns="columns"
      :loading="loading"
      :scroll="{ x: 1050 }"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchBills() } }"
      row-key="id"
      size="middle"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ (query.page - 1) * query.page_size + index + 1 }}</template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉 -->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="55vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="收支类型">
          <a-select v-model:value="mobileFilter.bill_type" placeholder="全部" allow-clear style="width:100%">
            <a-select-option value="income">收入</a-select-option>
            <a-select-option value="expense">支出</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="账户">
          <a-select v-model:value="mobileFilter.account_id" placeholder="全部账户" allow-clear style="width:100%">
            <a-select-option v-for="a in accounts" :key="a.id" :value="a.id">{{ a.name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="日期范围">
          <a-range-picker value-format="YYYY-MM-DD" style="width:100%"
            @change="(dates: string[]) => { mobileFilter.start_date = dates?.[0]; mobileFilter.end_date = dates?.[1] }" />
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
      title="账单详情"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerViewData">
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="收支类型">
              <a-tag :color="drawerViewData.bill_type === 'income' ? 'green' : 'red'">{{ drawerViewData.bill_type === 'income' ? '收入' : '支出' }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="收支类目">{{ drawerViewData.income_type ?? drawerViewData.expense_type ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="金额">
              <span :style="{ color: drawerViewData.bill_type === 'income' ? '#10b981' : '#ef4444', fontWeight: 600 }">
                {{ drawerViewData.bill_type === 'income' ? '+' : '-' }}¥{{ Number(drawerViewData.amount).toLocaleString() }}
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="账户">{{ drawerViewData.account_name ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="关联订单">{{ drawerViewData.order_no ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="日期">{{ drawerViewData.bill_date }}</a-descriptions-item>
            <a-descriptions-item label="备注">{{ drawerViewData.notes ?? '-' }}</a-descriptions-item>
          </a-descriptions>
        </template>
      </a-spin>
    </a-drawer>

    <a-drawer
      :title="editingId ? '编辑账单' : '录入账单'"
      :open="drawerOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="drawerOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="收支类型">
          <a-radio-group v-model:value="form.bill_type" @change="onBillTypeChange">
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
        <a-form-item v-if="form.bill_type === 'income' || form.bill_type === 'expense'" label="关联订单">
          <a-select v-model:value="form.customer_order_id" allow-clear placeholder="请选择关联订单（可选）" style="width:100%" @change="onOrderChange">
            <a-select-option v-for="o in orderOptions" :key="o.id" :value="o.id">{{ o.order_no }} · {{ o.customer_name }}</a-select-option>
          </a-select>
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
        <a-space style="width:100%;justify-content:flex-end">
          <a-button @click="drawerOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
