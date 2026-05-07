<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useBreakpoint } from '@/composables/useBreakpoint'
import { itineraryApi } from '@/api/itinerary'
import { numberToChineseMoney } from '@/utils/money'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { publicContractApi } from '@/api/contract'
import SignaturePad from '@/components/SignaturePad.vue'
import ImageMultiUpload from '@/components/ImageMultiUpload.vue'

const route = useRoute()
const token = route.params.token as string

const step = ref(0)  // 0:验证 1:阅读 2:签名 3:上传证件 4:完成
const contract = ref<any>(null)
const itinerary = ref<any>(null)
const phone = ref('')
const verifying = ref(false)
const signature = ref('')
const uploadedImages = ref<string[]>([])
const submitting = ref(false)
const errorMsg = ref('')
const { isMobile } = useBreakpoint()

onMounted(async () => {
  try {
    const res = await publicContractApi.getByToken(token)
    if (!res || !res.data) {
      errorMsg.value = '签署链接无效或已过期'
      return
    }
    contract.value = res.data
    // 动态获取行程明细
    if (contract.value?.customer_order_id) {
      try {
        const itinRes = await itineraryApi.list({ customer_order_id: contract.value.customer_order_id })
        const itins = Array.isArray(itinRes.data) ? itinRes.data : []
        itinerary.value = itins.length > 0 ? itins[0] : null
      } catch {
        itinerary.value = null
      }
    }
  } catch (err: any) {
    errorMsg.value = typeof err === 'string' ? err : '签署链接无效或已过期'
  }
})

async function verifyPhone() {
  verifying.value = true
  try {
    const res = await publicContractApi.verifyPhone(token, phone.value)
    if (!res || !res.data || !res.data.verified) {
      message.error('验证失败')
    } else {
      step.value = 1
    }
  } catch (err: any) {
    message.error(typeof err === 'string' ? err : '验证失败')
  } finally {
    verifying.value = false
  }
}

async function submitSign() {
  if (!signature.value) {
    message.error('请先完成签名')
    return
  }
  if (!uploadedImages.value.length) {
    message.error('请上传证件图片')
    return
  }
  submitting.value = true
  try {
    // 假设后端已支持 images 字段
    const res = await publicContractApi.sign(token, signature.value, uploadedImages.value)
    if (!res || !res.data) {
      message.error('提交失败')
    } else {
      step.value = 4
    }
  } catch (err: any) {
    message.error(typeof err === 'string' ? err : '提交失败')
  } finally {
    submitting.value = false
  }
}

function handleUpload(field: string, docIndex: number, info: any) {
  if (info.file.status === 'done') {
    idDocs.value[docIndex][field as 'front_url' | 'back_url'] = info.file.response?.data?.file_url ?? ''
  }
}
</script>

<template>
  <div :style="isMobile ? { maxWidth: '100vw', margin: '0', padding: '8px 0 16px' } : { maxWidth: '720px', margin: '40px auto', padding: '24px' }">
    <div v-if="errorMsg" style="text-align:center;color:red;font-size:18px;margin-top:80px">
      {{ errorMsg }}
    </div>
    <template v-else-if="contract">
      <!-- 步骤0：手机号验证 -->
      <a-card v-if="step === 0" title="合同签署 — 身份验证">
        <a-form-item label="请输入您的手机号进行身份验证">
          <a-input v-model:value="phone" placeholder="输入预留手机号" style="max-width:300px" />
        </a-form-item>
        <a-button type="primary" :loading="verifying" @click="verifyPhone">验证</a-button>
      </a-card>

      <!-- 步骤1：阅读合同（分割线分块，字段精简，金额大写，行程明细动态获取） -->
      <div v-else-if="step === 1"
        :style="isMobile
          ? { display: 'flex', flexDirection: 'column', gap: '0', padding: '0 8px' }
          : { display: 'flex', flexDirection: 'column', gap: '0' }">
        <!-- 1. 基本信息 -->
        <div>
          <div :style="isMobile ? { fontWeight: 600, fontSize: '15px', marginBottom: '6px' } : { fontWeight: 600, fontSize: '16px', marginBottom: '8px' }">基本信息</div>
          <a-descriptions :column="isMobile ? 1 : 2" size="small" bordered :style="isMobile ? { fontSize: '15px' } : {}">
            <a-descriptions-item label="出行人数">{{ contract.pax }}</a-descriptions-item>
            <a-descriptions-item label="出发日期">{{ contract.departure_date }}</a-descriptions-item>
            <a-descriptions-item label="返回日期">{{ contract.return_date }}</a-descriptions-item>
            <a-descriptions-item label="甲方">{{ contract.party_a || contract.customer_name }}</a-descriptions-item>
            <a-descriptions-item label="甲方联系电话">{{ contract.party_a_phone || contract.customer_phone }}</a-descriptions-item>
            <a-descriptions-item label="乙方">{{ contract.party_b }}</a-descriptions-item>
            <a-descriptions-item label="乙方联系电话">{{ contract.party_b_phone }}</a-descriptions-item>
          </a-descriptions>
        </div>
        <a-divider :style="isMobile ? { margin: '14px 0 8px' } : { margin: '18px 0 12px' }" />

        <!-- 2. 款项信息 -->
        <div>
          <div :style="isMobile ? { fontWeight: 600, fontSize: '15px', marginBottom: '6px' } : { fontWeight: 600, fontSize: '16px', marginBottom: '8px' }">款项信息</div>
          <a-descriptions :column="isMobile ? 1 : 2" size="small" bordered :style="isMobile ? { fontSize: '15px' } : {}">
            <a-descriptions-item label="合同总金额">¥{{ contract.total_amount }}</a-descriptions-item>
            <a-descriptions-item label="金额大写">{{ numberToChineseMoney(contract.total_amount) }}</a-descriptions-item>
            <a-descriptions-item label="定金">¥{{ contract.deposit_amount }}</a-descriptions-item>
            <a-descriptions-item label="定金到账日期">{{ contract.deposit_due_date }}</a-descriptions-item>
            <a-descriptions-item label="尾款">¥{{ contract.balance_amount }}</a-descriptions-item>
            <a-descriptions-item label="尾款到账日期">{{ contract.balance_due_date }}</a-descriptions-item>
          </a-descriptions>
        </div>
        <a-divider :style="isMobile ? { margin: '14px 0 8px' } : { margin: '18px 0 12px' }" />

        <!-- 3. 行程明细（动态获取，无数据则隐藏） -->
        <div v-if="itinerary && itinerary.days_detail && itinerary.days_detail.length">
          <div :style="isMobile ? { fontWeight: 600, fontSize: '15px', marginBottom: '6px' } : { fontWeight: 600, fontSize: '16px', marginBottom: '8px' }">行程明细</div>
          <a-timeline :style="isMobile ? { paddingLeft: '2px' } : {}">
            <a-timeline-item v-for="day in itinerary.days_detail" :key="day.seq">
              <b>第 {{ day.seq }} 天 · {{ day.date }}</b>
              <div>{{ day.details }}</div>
              <div v-if="day.accommodation_area">住宿：{{ day.accommodation_area }}</div>
              <div v-if="day.notes">备注：{{ day.notes }}</div>
            </a-timeline-item>
          </a-timeline>
        </div>
        <a-divider v-if="itinerary && itinerary.days_detail && itinerary.days_detail.length" :style="isMobile ? { margin: '14px 0 8px' } : { margin: '18px 0 12px' }" />

        <!-- 4. 补充信息 -->
        <div>
          <div :style="isMobile ? { fontWeight: 600, fontSize: '15px', marginBottom: '6px' } : { fontWeight: 600, fontSize: '16px', marginBottom: '8px' }">补充信息</div>
          <a-descriptions :column="1" size="small" bordered :style="isMobile ? { fontSize: '15px' } : {}">
            <a-descriptions-item label="包含项目">{{ contract.includes }}</a-descriptions-item>
            <a-descriptions-item label="不含项目">{{ contract.excludes }}</a-descriptions-item>
            <a-descriptions-item label="退改规则">{{ contract.cancellation_policy }}</a-descriptions-item>
            <a-descriptions-item v-if="contract.travel_notice" label="出行提示">{{ contract.travel_notice }}</a-descriptions-item>
            <a-descriptions-item v-if="contract.notes" label="备注">{{ contract.notes }}</a-descriptions-item>
          </a-descriptions>
        </div>

        <a-button type="primary"
          :style="isMobile ? { marginTop: '14px', width: '100%', height: '40px', fontSize: '16px', borderRadius: '6px' } : { marginTop: '16px' }"
          @click="step = 2">
          已阅读，前往签名
        </a-button>
      </div>

      <!-- 步骤2：签名 -->
      <a-card v-else-if="step === 2" title="电子签名">
        <SignaturePad @signed="(data: string) => (signature = data)" />
        <a-space style="margin-top:16px">
          <a-button @click="step = 1">返回</a-button>
          <a-button type="primary" :disabled="!signature" @click="step = 3">下一步：上传证件</a-button>
        </a-space>
      </a-card>

      <!-- 步骤3：上传证件（多文件图片上传） -->
      <a-card v-else-if="step === 3" title="上传证件">
        <div style="margin-bottom:16px">
          <ImageMultiUpload v-model="uploadedImages" :max-count="20" :max-size-m-b="10" :data="{ scene: 'contract' }" />
        </div>
        <a-space style="margin-top:8px">
          <a-button @click="step = 2">返回</a-button>
          <a-button type="primary" :loading="submitting" @click="submitSign">提交完成签署</a-button>
        </a-space>
      </a-card>

      <!-- 步骤4：完成 -->
      <a-result v-else status="success" title="签署完成" sub-title="您的合同已成功签署，感谢您的确认！" />
    </template>
  </div>
</template>
