<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Modal, message } from 'ant-design-vue'
import { contractApi } from '@/api/contract'
import { orderApi } from '@/api/order'
import { productApi } from '@/api/product'
import { itineraryApi } from '@/api/itinerary'

const emit = defineEmits<{ saved: [id: number]; cancel: [] }>()
const props = defineProps<{ showFooter?: boolean; editId?: number | null }>()

const router = useRouter()
const loading = ref(false)
const loadingProduct = ref(false)
const orderId = ref<number | undefined>()
const editOrderNo = ref('')
const orderOptions = ref<{ id: number; label: string }[]>([])

const includes = ref('')
const excludes = ref('')
const travelNotice = ref('')
const cancellationPolicy = ref('')
const notes = ref('')
// 新增甲乙方及联系电话字段
const partyA = ref('')
const partyAPhone = ref('')
const partyB = ref('')
const partyBPhone = ref('')

onMounted(async () => {
  if (props.editId) {
    loading.value = true
    try {
      const res = await contractApi.get(props.editId)
      const c = res.data as any
      editOrderNo.value = c.order_no ?? ''
      includes.value = c.includes ?? ''
      excludes.value = c.excludes ?? ''
      travelNotice.value = c.travel_notice ?? ''
      cancellationPolicy.value = c.cancellation_policy ?? ''
      notes.value = c.notes ?? ''
      partyA.value = c.party_a ?? c.customer_name ?? ''
      partyAPhone.value = c.party_a_phone ?? c.customer_phone ?? ''
      partyB.value = c.party_b ?? ''
      partyBPhone.value = c.party_b_phone ?? ''
    } finally {
      loading.value = false
    }
  } else {
    const [ordersRes, contractsRes] = await Promise.all([
      orderApi.list({ page_size: 999 }),
      contractApi.list({ page_size: 999 }),
    ])
    const orders = Array.isArray(ordersRes.data) ? ordersRes.data : (ordersRes.data?.items ?? [])
    const contracts = Array.isArray(contractsRes.data) ? contractsRes.data : (contractsRes.data?.items ?? [])
    const contractedOrderIds = new Set(
      contracts.map((c: any) => c.customer_order_id).filter(Boolean)
    )
    orderOptions.value = orders
      .filter((o: any) => !contractedOrderIds.has(o.id))
      .map((o: any) => ({ id: o.id, label: `${o.order_no} · ${o.customer_name} · ${o.product_name ?? ''}` }))
  }
})

function resetFields() {
  includes.value = ''
  excludes.value = ''
  travelNotice.value = ''
  cancellationPolicy.value = ''
  notes.value = ''
  partyA.value = ''
  partyAPhone.value = ''
  partyB.value = ''
  partyBPhone.value = ''
}

async function onOrderChange(id: number | undefined) {
  resetFields()
  if (!id) return
  loadingProduct.value = true
  try {
    const itinRes = await itineraryApi.list({ customer_order_id: id })
    const itinData = itinRes.data ?? []
    const itins = Array.isArray(itinData) ? itinData : (itinData as any).items ?? []
    if (itins.length === 0) {
      const confirmed = await new Promise<boolean>(resolve => {
        Modal.confirm({
          title: '该订单尚未创建行程',
          content: '该订单尚未创建行程，是否继续创建合同？',
          okText: '继续',
          cancelText: '取消',
          onOk: () => resolve(true),
          onCancel: () => resolve(false),
        })
      })
      if (!confirmed) {
        orderId.value = undefined
        return
      }
    }
    const orderRes = await orderApi.get(id)
    const order = orderRes.data
    // 自动填充甲方及电话
    partyA.value = order?.customer_name ?? ''
    partyAPhone.value = order?.customer_phone ?? ''
    if (order?.product_id) {
      const prodRes = await productApi.get(order.product_id)
      const prod = prodRes.data
      includes.value = prod.includes ?? ''
      excludes.value = prod.excludes ?? ''
      travelNotice.value = prod.travel_notice ?? ''
      cancellationPolicy.value = prod.cancellation_policy ?? ''
    }
  } finally {
    loadingProduct.value = false
  }
}

async function save() {
  if (props.editId) {
    loading.value = true
    try {
      await contractApi.update(props.editId, {
        includes: includes.value || null,
        excludes: excludes.value || null,
        travel_notice: travelNotice.value || null,
        cancellation_policy: cancellationPolicy.value || null,
        notes: notes.value || null,
        party_a: partyA.value || null,
        party_a_phone: partyAPhone.value || null,
        party_b: partyB.value || null,
        party_b_phone: partyBPhone.value || null,
      })
      message.success('合同已保存')
      emit('saved', props.editId)
      router.push(`/contracts/${props.editId}`)
    } finally {
      loading.value = false
    }
  } else {
    if (!orderId.value) { message.error('请选择关联订单'); return }
    loading.value = true
    try {
      const res = await contractApi.create({
        customer_order_id: orderId.value,
        includes: includes.value || null,
        excludes: excludes.value || null,
        travel_notice: travelNotice.value || null,
        cancellation_policy: cancellationPolicy.value || null,
        party_a: partyA.value || null,
        party_a_phone: partyAPhone.value || null,
        party_b: partyB.value || null,
        party_b_phone: partyBPhone.value || null,
      })
      message.success('合同已创建')
      emit('saved', res.data.id)
    } finally {
      loading.value = false
    }
  }
}

function handleCancel() {
  if (props.editId) {
    router.back()
  } else {
    emit('cancel')
  }
}

defineExpose({
  resetForm: () => {
    orderId.value = undefined
    resetFields()
  },
  save,
  loading,
})
</script>

<template>
  <a-form layout="vertical">
    <!-- 订单选择项始终置于最顶部 -->
    <a-form-item v-if="!props.editId" label="关联订单" required>
      <a-select
        v-model:value="orderId"
        placeholder="请选择订单（仅显示未创建合同的订单）"
        style="width:100%"
        show-search
        :filter-option="(input: string, opt: any) => opt.label?.toLowerCase().includes(input.toLowerCase())"
        @change="onOrderChange"
      >
        <a-select-option v-for="o in orderOptions" :key="o.id" :value="o.id" :label="o.label">
          {{ o.label }}
        </a-select-option>
      </a-select>
    </a-form-item>
    <a-form-item v-else label="关联订单">
      <span style="color:#333">{{ editOrderNo }}</span>
    </a-form-item>

    <!-- 甲乙方及联系方式同排（PC）/换行（移动） -->
    <a-row :gutter="16">
      <a-col :xs="24" :md="12">
        <a-form-item label="甲方" required>
          <a-input v-model:value="partyA" placeholder="请输入甲方名称（自动从订单带入，可编辑）" :disabled="!orderId && !props.editId" />
        </a-form-item>
      </a-col>
      <a-col :xs="24" :md="12">
        <a-form-item label="甲方联系电话" required>
          <a-input v-model:value="partyAPhone" placeholder="请输入甲方联系电话（自动从订单带入，可编辑）" :disabled="!orderId && !props.editId" />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :xs="24" :md="12">
        <a-form-item label="乙方">
          <a-input v-model:value="partyB" placeholder="请输入乙方名称" :disabled="!orderId && !props.editId" />
        </a-form-item>
      </a-col>
      <a-col :xs="24" :md="12">
        <a-form-item label="乙方联系电话">
          <a-input v-model:value="partyBPhone" placeholder="请输入乙方联系电话" :disabled="!orderId && !props.editId" />
        </a-form-item>
      </a-col>
    </a-row>
    <a-spin :spinning="loadingProduct">
      <a-form-item label="费用包含">
        <a-textarea v-model:value="includes" :rows="3" placeholder="从产品自动填入，可编辑" :disabled="!orderId && !props.editId" />
      </a-form-item>
      <a-form-item label="费用不含">
        <a-textarea v-model:value="excludes" :rows="3" placeholder="从产品自动填入，可编辑" :disabled="!orderId && !props.editId" />
      </a-form-item>
      <a-form-item label="出行提示">
        <a-textarea v-model:value="travelNotice" :rows="3" placeholder="从产品自动填入，可编辑" :disabled="!orderId && !props.editId" />
      </a-form-item>
      <a-form-item label="取消政策">
        <a-textarea v-model:value="cancellationPolicy" :rows="3" placeholder="从产品自动填入，可编辑" :disabled="!orderId && !props.editId" />
      </a-form-item>
    </a-spin>
    <a-form-item label="备注">
      <a-textarea v-model:value="notes" :rows="2" placeholder="备注信息" :disabled="!orderId && !props.editId" />
    </a-form-item>
  </a-form>
  <div v-if="props.showFooter !== false" style="margin-top:24px;display:flex;justify-content:flex-end">
    <a-space>
      <a-button @click="handleCancel">取消</a-button>
      <a-button type="primary" :loading="loading" @click="save">{{ props.editId ? '保存' : '创建合同' }}</a-button>
    </a-space>
  </div>
</template>
