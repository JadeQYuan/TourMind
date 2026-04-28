import { writeFileSync } from 'fs'
import { join } from 'path'

const src = 'e:/Code/TourMind/frontend/src'

writeFileSync(join(src, 'views/product/ProductListView.vue'), `<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { productApi } from '@/api/product'
import type { Product, ProductListItem, ProductTemplateDay } from '@/types'

const windowWidth = ref(window.innerWidth)
window.addEventListener('resize', () => { windowWidth.value = window.innerWidth })

const products = ref<ProductListItem[]>([])
const loading = ref(false)
const query = reactive({ keyword: '', status: undefined as string | undefined })
const drawerOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<Product>>({ status: 'active', itinerary_template: [] })

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await productApi.list(query)
  products.value = res.data ?? []
  loading.value = false
}

function openCreate() {
  editingId.value = null
  form.value = { status: 'active', itinerary_template: [] }
  drawerOpen.value = true
}

async function openEdit(id: number) {
  const res = await productApi.get(id)
  editingId.value = id
  form.value = { ...res.data }
  drawerOpen.value = true
}

function addTemplateDay() {
  const days = form.value.itinerary_template ?? []
  form.value.itinerary_template = [...days, { seq: days.length + 1, details: '', accommodation_area: null, notes: null }]
}

function removeTemplateDay(index: number) {
  const days = [...(form.value.itinerary_template ?? [])]
  days.splice(index, 1)
  form.value.itinerary_template = days.map((d, i) => ({ ...d, seq: i + 1 }))
}

async function save() {
  if (!form.value.name?.trim()) { message.error('请输入产品名称'); return }
  if (!form.value.destination?.trim()) { message.error('请输入目的地'); return }
  if (!form.value.days || form.value.days < 1) { message.error('请输入正确的天数'); return }

  const payload = { ...form.value } as any
  if (editingId.value) {
    await productApi.update(editingId.value, payload)
  } else {
    await productApi.create(payload)
  }
  drawerOpen.value = false
  message.success('保存成功')
  fetchList()
}

async function doCopy(id: number) {
  await productApi.copy(id)
  message.success('复制成功')
  fetchList()
}

async function doDelete(id: number) {
  Modal.confirm({
    title: '确认删除此产品？',
    content: '删除后不可恢复。',
    okType: 'danger',
    onOk: async () => { await productApi.delete(id); fetchList() },
  })
}

const columns = [
  { title: '产品名称', dataIndex: 'name', width: 200, ellipsis: true },
  { title: '目的地', dataIndex: 'destination', width: 130, ellipsis: true },
  { title: '天数', dataIndex: 'days', width: 60, align: 'center' as const },
  { title: '参考价(元)', dataIndex: 'reference_price', width: 110, align: 'right' as const,
    customRender: ({ text }: any) => text != null ? \`¥\${Number(text).toLocaleString()}\` : '-' },
  { title: '状态', dataIndex: 'status', width: 70, align: 'center' as const },
  { title: '操作', key: 'action', width: 140 },
]
</script>

<template>
  <div style="padding:24px">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form layout="inline">
        <a-form-item label="名称">
          <a-input v-model:value="query.keyword" placeholder="搜索产品名称" allow-clear @change="fetchList" style="width:180px" />
        </a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="query.status" placeholder="全部" allow-clear style="width:90px" @change="fetchList">
            <a-select-option value="active">上架</a-select-option>
            <a-select-option value="inactive">下架</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="fetchList">查询</a-button>
        </a-form-item>
      </a-form>
      <a-button type="primary" @click="openCreate">新增产品</a-button>
    </div>

    <a-table
      :data-source="products"
      :columns="columns"
      :loading="loading"
      :pagination="false"
      row-key="id"
      size="small"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex === 'status'">
          <a-tag :color="record.status === 'active' ? 'green' : 'default'">
            {{ record.status === 'active' ? '上架' : '下架' }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openEdit(record.id)">编辑</a-button>
            <a-button size="small" @click="doCopy(record.id)">复制</a-button>
            <a-button size="small" danger @click="doDelete(record.id)">删除</a-button>
          </a-space>
        </template>
      </template>
    </a-table>

    <!-- 表单抽屉 -->
    <a-drawer
      :title="editingId ? '编辑产品' : '新增产品'"
      :open="drawerOpen"
      :width="Math.min(620, windowWidth)"
      placement="right"
      @close="drawerOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="产品名称" required>
          <a-input v-model:value="form.name" placeholder="请输入产品名称" />
        </a-form-item>
        <a-row :gutter="12">
          <a-col :span="12">
            <a-form-item label="目的地" required>
              <a-input v-model:value="form.destination" placeholder="如：桂林" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="状态">
              <a-select v-model:value="form.status" style="width:100%">
                <a-select-option value="active">上架</a-select-option>
                <a-select-option value="inactive">下架</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
        </a-row>
        <a-row :gutter="12">
          <a-col :span="12">
            <a-form-item label="天数" required>
              <a-input-number v-model:value="form.days" :min="1" :max="365" style="width:100%" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="参考价格（元）">
              <a-input-number v-model:value="form.reference_price" :min="0" :precision="2" style="width:100%" />
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
          <a-textarea v-model:value="form.notes" :rows="2" />
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
            <a-col :span="12">
              <a-input v-model:value="day.accommodation_area" placeholder="住宿区域（选填）" />
            </a-col>
            <a-col :span="12">
              <a-input v-model:value="day.notes" placeholder="备注（选填）" />
            </a-col>
          </a-row>
        </div>
        <a-button type="dashed" style="width:100%;margin-top:4px" @click="addTemplateDay">+ 添加一天</a-button>
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
console.log('ProductListView.vue written')
