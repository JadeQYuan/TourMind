<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { message } from 'ant-design-vue'
import { publicContractApi } from '@/api/contract'
import SignaturePad from '@/components/SignaturePad.vue'

const route = useRoute()
const token = route.params.token as string

const step = ref(0)  // 0:验证 1:阅读 2:签名 3:上传证件 4:完成
const contract = ref<any>(null)
const phone = ref('')
const verifying = ref(false)
const signature = ref('')
const idDocs = ref([{ name: '', id_type: 'id_card', id_no: '', front_url: '', back_url: '' }])
const submitting = ref(false)
const errorMsg = ref('')

onMounted(async () => {
  const res = await publicContractApi.getByToken(token)
  if (res.code !== 0) {
    errorMsg.value = '签署链接无效或已过期'
  } else {
    contract.value = res.data
  }
})

async function verifyPhone() {
  verifying.value = true
  try {
    const res = await publicContractApi.verifyPhone(token, phone.value)
    if (res.code !== 0) {
      message.error(res.message || '验证失败')
    } else {
      step.value = 1
    }
  } finally {
    verifying.value = false
  }
}

async function submitSign() {
  if (!signature.value) {
    message.error('请先完成签名')
    return
  }
  submitting.value = true
  try {
    const res = await publicContractApi.sign(token, signature.value, idDocs.value)
    if (res.code !== 0) {
      message.error(res.message || '提交失败')
    } else {
      step.value = 4
    }
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
  <div style="max-width:720px;margin:40px auto;padding:24px">
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

      <!-- 步骤1：阅读合同 -->
      <a-card v-else-if="step === 1" title="合同详情">
        <a-descriptions bordered :column="2" size="small">
          <a-descriptions-item label="客户">{{ contract.customer_name }}</a-descriptions-item>
          <a-descriptions-item label="出行人数">{{ contract.pax }}</a-descriptions-item>
          <a-descriptions-item label="出发日期">{{ contract.departure_date }}</a-descriptions-item>
          <a-descriptions-item label="返回日期">{{ contract.return_date }}</a-descriptions-item>
          <a-descriptions-item label="合同总金额" :span="2">¥{{ contract.total_amount }}</a-descriptions-item>
          <a-descriptions-item label="包含项目" :span="2">{{ contract.includes }}</a-descriptions-item>
          <a-descriptions-item label="不含项目" :span="2">{{ contract.excludes }}</a-descriptions-item>
          <a-descriptions-item label="退改规则" :span="2">{{ contract.cancellation_policy }}</a-descriptions-item>
          <a-descriptions-item v-if="contract.travel_notice" label="出行提示" :span="2">{{ contract.travel_notice }}</a-descriptions-item>
        </a-descriptions>

        <a-divider>行程明细</a-divider>
        <a-timeline>
          <a-timeline-item v-for="day in contract.days_detail" :key="day.day_number">
            <b>第 {{ day.day_number }} 天 · {{ day.date }}</b>
            <div>{{ day.details }}</div>
            <div v-if="day.accommodation_area">住宿：{{ day.accommodation_area }}</div>
          </a-timeline-item>
        </a-timeline>

        <a-button type="primary" style="margin-top:16px" @click="step = 2">
          已阅读，前往签名
        </a-button>
      </a-card>

      <!-- 步骤2：签名 -->
      <a-card v-else-if="step === 2" title="电子签名">
        <SignaturePad @signed="(data: string) => (signature = data)" />
        <a-space style="margin-top:16px">
          <a-button @click="step = 1">返回</a-button>
          <a-button type="primary" :disabled="!signature" @click="step = 3">下一步：上传证件</a-button>
        </a-space>
      </a-card>

      <!-- 步骤3：上传证件 -->
      <a-card v-else-if="step === 3" title="上传证件">
        <div v-for="(doc, i) in idDocs" :key="i" style="border:1px solid #f0f0f0;padding:16px;margin-bottom:12px;border-radius:4px">
          <a-row :gutter="16">
            <a-col :span="8">
              <a-form-item label="姓名">
                <a-input v-model:value="doc.name" />
              </a-form-item>
            </a-col>
            <a-col :span="6">
              <a-form-item label="证件类型">
                <a-select v-model:value="doc.id_type">
                  <a-select-option value="id_card">身份证</a-select-option>
                  <a-select-option value="passport">护照</a-select-option>
                  <a-select-option value="hk_pass">港澳通行证</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="10">
              <a-form-item label="证件号码">
                <a-input v-model:value="doc.id_no" />
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="证件正面">
                <a-upload
                  action="/api/v1/files/upload"
                  :data="{ scene: 'contract', related_id: '0' }"
                  list-type="picture-card"
                  :max-count="1"
                  @change="(info: any) => handleUpload('front_url', i, info)"
                >
                  <div v-if="!doc.front_url"><plus-outlined /><div>上传</div></div>
                </a-upload>
              </a-form-item>
            </a-col>
            <a-col :span="12" v-if="doc.id_type === 'id_card'">
              <a-form-item label="证件反面">
                <a-upload
                  action="/api/v1/files/upload"
                  :data="{ scene: 'contract', related_id: '0' }"
                  list-type="picture-card"
                  :max-count="1"
                  @change="(info: any) => handleUpload('back_url', i, info)"
                >
                  <div v-if="!doc.back_url"><plus-outlined /><div>上传</div></div>
                </a-upload>
              </a-form-item>
            </a-col>
          </a-row>
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
