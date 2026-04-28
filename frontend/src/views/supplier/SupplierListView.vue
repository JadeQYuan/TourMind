<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { FilterOutlined } from '@ant-design/icons-vue'
const windowWidth = ref(window.innerWidth)
import { supplierApi } from '@/api/supplier'
import type { Supplier } from '@/types'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const suppliers = ref<Supplier[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ keyword: '', is_active: true as boolean | undefined, page: 1, page_size: 20 })
const modalOpen = ref(false)
const editingId = ref<number | null>(null)
const form = ref<Partial<Supplier>>({ is_active: true })

const drawerViewOpen = ref(false)
const drawerViewData = ref<Supplier | null>(null)
const drawerLoading = ref(false)

onMounted(fetchList)

async function fetchList() {
  loading.value = true
  const res = await supplierApi.list(query)
  suppliers.value = res.data?.items ?? res.data ?? []
  total.value = res.data?.total ?? suppliers.value.length
  loading.value = false
}

function openCreate() { editingId.value = null; form.value = { is_active: true }; modalOpen.value = true }
function openEdit(s: Supplier) { editingId.value = s.id; form.value = { ...s, contact_person: s.contact_person ?? undefined, contact_phone: s.contact_phone ?? undefined, notes: s.notes ?? undefined }; modalOpen.value = true }

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

async function openViewDrawer(id: number) {
  drawerViewOpen.value = true
  drawerViewData.value = null
  drawerLoading.value = true
  try {
    const res = await supplierApi.get(id)
    drawerViewData.value = res.data
  } catch {
    message.error('加载失败')
    drawerViewOpen.value = false
  } finally {
    drawerLoading.value = false
  }
}

async function toggleActive(record: Supplier) {
  await supplierApi.update(record.id, { is_active: !record.is_active })
  message.success(record.is_active ? '已停用' : '已启用')
  fetchList()
}

const mobileFilterOpen = ref(false)
const mobileFilter = reactive({ keyword: '', is_active: true as boolean | undefined })

const activeFilterCount = computed(() => {
  let n = 0
  if (query.keyword) n++
  if (query.is_active !== true) n++
  return n
})

function openMobileFilter() {
  mobileFilter.keyword = query.keyword
  mobileFilter.is_active = query.is_active
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  query.keyword = mobileFilter.keyword
  query.is_active = mobileFilter.is_active
  query.page = 1
  mobileFilterOpen.value = false
  fetchList()
}

function resetMobileFilter() {
  mobileFilter.keyword = ''
  mobileFilter.is_active = true
}

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '名称', dataIndex: 'name', width: 200, ellipsis: true },
  { title: '联系人', dataIndex: 'contact_person', width: 100 },
  { title: '联系电话', dataIndex: 'contact_phone', width: 140 },
  { title: '备注', dataIndex: 'notes', width: 180, ellipsis: true },
  { title: '状态', key: 'is_active', width: 80, align: 'center' },
  { title: '操作', key: 'action', width: 160, fixed: 'right' as const },
]
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form v-if="!isMobile" layout="inline">
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
          <a-button @click="() => { query.keyword = ''; query.is_active = true; query.page = 1; fetchList() }">重置</a-button>
        </a-form-item>
      </a-form>
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter"><template #icon><filter-outlined /></template>筛选</a-button>
      </a-badge>
      <a-button type="primary" @click="openCreate">新增供应商</a-button>
    </div>

    <!-- 移动端卡片 -->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="suppliers" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;color:#111827;font-size:14px">{{ record.name }}</div>
                    <div v-if="record.contact_person" style="font-size:13px;color:#6b7280;margin-top:2px">联系人：{{ record.contact_person }}</div>
                    <div v-if="record.contact_phone" style="font-size:13px;color:#6b7280;margin-top:2px">电话：{{ record.contact_phone }}</div>
                  </div>
                  <a-tag :color="record.is_active ? 'green' : 'default'" style="margin:0">{{ record.is_active ? '启用' : '停用' }}</a-tag>
                </div>
                <div style="display:flex;justify-content:flex-end;gap:6px;margin-top:8px">
                  <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
                  <a-button size="small" @click="openEdit(record)">编辑</a-button>
                  <a-button size="small" @click="toggleActive(record)">{{ record.is_active ? '停用' : '启用' }}</a-button>
                </div>
              </a-card>
            </a-list-item>
          </template>
        </a-list>
        <div style="display:flex;justify-content:center;margin-top:12px">
          <a-pagination :total="total" :current="query.page" :page-size="query.page_size" size="small" :show-size-changer="false"
            @change="(p: number) => { query.page = p; fetchList() }" />
        </div>
      </a-spin>
    </template>

    <!-- 桌面端表格 -->
    <a-table v-else :data-source="suppliers" :columns="columns" :loading="loading"
      :scroll="{ x: 900 }"
      :pagination="{ total, current: query.page, pageSize: query.page_size, onChange: (p: number) => { query.page = p; fetchList() } }"
      row-key="id" size="middle">
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ (query.page - 1) * query.page_size + index + 1 }}</template>
        <template v-else-if="column.key === 'is_active'">
          <a-tag :color="record.is_active ? 'green' : 'default'">{{ record.is_active ? '启用' : '停用' }}</a-tag>
        </template>
        <template v-else-if="column.key === 'action'">
          <a-space>
            <a-button size="small" @click="openViewDrawer(record.id)">查看</a-button>
            <a-button size="small" @click="openEdit(record)">编辑</a-button>
            <a-button size="small" @click="toggleActive(record)">{{ record.is_active ? '停用' : '启用' }}</a-button>
          </a-space>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉 -->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="45vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="名称"><a-input v-model:value="mobileFilter.keyword" placeholder="搜索供应商名称" allow-clear /></a-form-item>
        <a-form-item label="状态">
          <a-select v-model:value="mobileFilter.is_active" placeholder="全部" allow-clear style="width:100%">
            <a-select-option :value="true">启用</a-select-option>
            <a-select-option :value="false">停用</a-select-option>
          </a-select>
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
      title="供应商详情"
      :open="drawerViewOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="drawerViewOpen = false"
    >
      <a-spin :spinning="drawerLoading">
        <template v-if="drawerViewData">
          <a-descriptions :column="1" bordered size="small">
            <a-descriptions-item label="名称">{{ drawerViewData.name }}</a-descriptions-item>
            <a-descriptions-item label="联系人">{{ drawerViewData.contact_person ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="联系电话">{{ drawerViewData.contact_phone ?? '-' }}</a-descriptions-item>
            <a-descriptions-item label="备注">
              <span style="white-space:pre-wrap">{{ drawerViewData.notes ?? '-' }}</span>
            </a-descriptions-item>
            <a-descriptions-item label="状态">
              <a-tag :color="drawerViewData.is_active ? 'green' : 'default'">{{ drawerViewData.is_active ? '启用' : '停用' }}</a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="创建时间">{{ drawerViewData.created_at?.slice(0, 16).replace('T', ' ') }}</a-descriptions-item>
          </a-descriptions>
        </template>
      </a-spin>
    </a-drawer>

    <a-drawer
      :title="editingId ? '编辑供应商' : '新增供应商'"
      :open="modalOpen"
      :width="isMobile ? '100%' : Math.min(480, windowWidth)"
      placement="right"
      @close="modalOpen = false"
    >
      <a-form layout="vertical">
        <a-form-item label="名称" required><a-input v-model:value="form.name" /></a-form-item>
        <a-form-item label="联系人"><a-input v-model:value="form.contact_person" /></a-form-item>
        <a-form-item label="联系电话"><a-input v-model:value="form.contact_phone" /></a-form-item>
        <a-form-item label="备注"><a-textarea v-model:value="form.notes" :rows="3" /></a-form-item>
      </a-form>
      <template #footer>
        <a-space style="width:100%;justify-content:flex-end">
          <a-button @click="modalOpen = false">取消</a-button>
          <a-button type="primary" @click="save">保存</a-button>
        </a-space>
      </template>
    </a-drawer>
  </div>
</template>
