<script setup lang="ts">
function copyShareLink() {
  if (shareLink.value) {
    navigator.clipboard.writeText(shareLink.value)
      .then(() => message.success('已复制'))
      .catch(() => message.error('复制失败'))
  }
}
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { contractApi } from '@/api/contract'
import type { Contract } from '@/types'

const route = useRoute()
const router = useRouter()
const id = Number(route.params.id)

const contract = ref<Contract | null>(null)
const loading = ref(true)
const shareLink = ref('')

const STATUS_LABEL: Record<string, string> = {
  pending_sign: '待签署', signed: '已签署',
  revoked: '已撤销',
}
const STATUS_COLOR: Record<string, string> = {
  pending_sign: 'blue', signed: 'cyan',
  revoked: 'error',
}

onMounted(async () => {
  const res = await contractApi.get(id)
  contract.value = res.data
  if (contract.value?.share_token) {
    shareLink.value = `${location.origin}/sign/${contract.value.share_token}`
  }
  loading.value = false
})

async function changeStatus(status: string) {
  await contractApi.updateStatus(id, status)
  message.success('状态已更新')
  router.back()
}
</script>

<template>
  <div style="padding:24px">
    <a-page-header
      title="合同详情"
      :sub-title="contract?.contract_no"
      @back="router.back()"
    />
    <a-spin :spinning="loading">
      <template v-if="contract">
        <!-- Status + Actions -->
        <a-card style="margin-bottom:16px">
          <a-space wrap>
            <a-tag :color="STATUS_COLOR[contract.status]">{{ STATUS_LABEL[contract.status] }}</a-tag>
            <a-button danger v-if="contract.status === 'pending_sign'" @click="changeStatus('revoked')">撤销合同</a-button>
            <a-button @click="router.push(`/contracts/${id}/edit`)">编辑</a-button>
          </a-space>
          <div v-if="shareLink" style="margin-top:12px">
            <span style="color:#666;margin-right:8px">客户签署链接：</span>
            <a :href="shareLink" target="_blank">{{ shareLink }}</a>
            <a-button type="link" size="small"
              @click="copyShareLink">复制</a-button>
          </div>
        </a-card>

        <!-- Basic Info -->
        <a-card title="基本信息" style="margin-bottom:16px">
          <a-descriptions :column="isPC ? 3 : 1" bordered size="small">
            <a-descriptions-item label="关联订单" :span="isPC ? 3 : 1">{{ contract.order_no }}</a-descriptions-item>
            <a-descriptions-item label="甲方">{{ contract.party_a || contract.customer_name }}</a-descriptions-item>
            <a-descriptions-item label="甲方联系电话">{{ contract.party_a_phone || contract.customer_phone }}</a-descriptions-item>
            <a-descriptions-item label="乙方">{{ contract.party_b }}</a-descriptions-item>
            <a-descriptions-item label="乙方联系电话">{{ contract.party_b_phone }}</a-descriptions-item>
            <a-descriptions-item label="出行人数">{{ contract.pax }}</a-descriptions-item>
            <a-descriptions-item v-if="contract.travelers?.length" label="出行人" :span="3">{{ (contract.travelers as any[]).map((t: any) => t.name).join('、') }}</a-descriptions-item>
            <a-descriptions-item label="出发日期">{{ contract.departure_date }}</a-descriptions-item>
            <a-descriptions-item label="返回日期">{{ contract.return_date }}</a-descriptions-item>
            <a-descriptions-item label="合同总额">¥{{ contract.total_amount }}</a-descriptions-item>
            <a-descriptions-item label="定金">¥{{ contract.deposit_amount }}</a-descriptions-item>
            <a-descriptions-item label="定金到账日期">{{ contract.deposit_due_date }}</a-descriptions-item>
            <a-descriptions-item label="尾款">¥{{ contract.balance_amount }}</a-descriptions-item>
            <a-descriptions-item label="尾款到账日期">{{ contract.balance_due_date }}</a-descriptions-item>
            <a-descriptions-item label="签署时间" :span="2">{{ contract.signed_at ?? '—' }}</a-descriptions-item>
          </a-descriptions>
        </a-card>

        <!-- 款项信息 -->
        <a-card title="款项信息" style="margin-bottom:16px">
          <a-descriptions :column="3" bordered size="small">
            <a-descriptions-item label="包含项目" :span="3">{{ contract.includes }}</a-descriptions-item>
            <a-descriptions-item label="不含项目" :span="3">{{ contract.excludes }}</a-descriptions-item>
            <a-descriptions-item label="退改规则" :span="3">{{ contract.cancellation_policy }}</a-descriptions-item>
            <a-descriptions-item v-if="contract.travel_notice" label="出行提示" :span="3">{{ contract.travel_notice }}</a-descriptions-item>
          </a-descriptions>
        </a-card>

        <!-- Bill Summary -->
        <a-card title="账单概览" style="margin-bottom:16px">
          <a-row :gutter="16">
            <a-col :span="6"><a-statistic title="合同总额" :value="contract.total_amount" prefix="¥" /></a-col>
            <a-col :span="6"><a-statistic title="已收款" :value="contract.bill_summary?.total_income ?? 0" prefix="¥" /></a-col>
            <a-col :span="6"><a-statistic title="待收款" :value="contract.bill_summary?.pending_income ?? 0" prefix="¥" /></a-col>
            <a-col :span="6"><a-statistic title="预估利润" :value="contract.bill_summary?.estimated_profit ?? 0" prefix="¥" /></a-col>
          </a-row>
          <a-button style="margin-top:12px" @click="router.push(`/bills?contract_id=${id}`)">查看关联账单</a-button>
        </a-card>

        <!-- Days -->
        <a-card title="行程明细">
          <a-timeline>
            <a-timeline-item v-for="day in contract.days_detail" :key="day.day_number">
              <b>第 {{ day.day_number }} 天 · {{ day.date }}</b>
              <div>{{ day.details }}</div>
              <div v-if="day.accommodation_area" style="color:#888">住宿：{{ day.accommodation_area }}</div>
            </a-timeline-item>
          </a-timeline>
        </a-card>

        <!-- Signature -->
        <a-card v-if="contract.signature_image_url" title="客户签名" style="margin-top:16px">
          <img :src="contract.signature_image_url" style="max-width:400px;border:1px solid #eee" />
        </a-card>

        <!-- Notes -->
        <a-card v-if="contract.notes" title="备注" style="margin-top:16px">
          <p style="white-space:pre-wrap;margin:0">{{ contract.notes }}</p>
        </a-card>
      </template>
    </a-spin>
  </div>
</template>
