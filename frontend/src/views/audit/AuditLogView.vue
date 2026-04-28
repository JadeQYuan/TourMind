<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { FilterOutlined } from '@ant-design/icons-vue'
import { userApi } from '@/api/user'
import { auditApi } from '@/api/audit'
import { useBreakpoint } from '@/composables/useBreakpoint'

const { isMobile } = useBreakpoint()

const items = ref<any[]>([])
const total = ref(0)
const loading = ref(false)
const query = reactive({ keyword: '', user_id: undefined as number | undefined, result: undefined as string | undefined, page: 1, page_size: 20 })

const userOptions = ref<{ id: number; full_name: string }[]>([])

const RESULT_COLOR: Record<string, string> = { success: 'green', failure: 'red' }
const RESULT_LABEL: Record<string, string> = { success: '成功', failure: '失败' }

const columns = [
  { title: '', key: '_seq', width: 55, align: 'center' as const },
  { title: '时间', dataIndex: 'created_at', width: 160, customRender: ({ text }: any) => text?.slice(0, 19).replace('T', ' ') },
  { title: '操作人', dataIndex: 'user_name', width: 90 },
  { title: '操作', dataIndex: 'action', width: 130 },
  { title: '对象', dataIndex: 'resource', width: 180, ellipsis: true },
  { title: 'IP 地址', dataIndex: 'ip', width: 130 },
  { title: '结果', key: 'result', width: 80, align: 'center' as const },
  { title: '详情', dataIndex: 'detail', width: 200, ellipsis: true },
]

onMounted(async () => {
  const res = await userApi.list({ page: 1, page_size: 100 })
  userOptions.value = (res.data?.items ?? res.data ?? []).map((u: any) => ({ id: u.id, full_name: u.full_name ?? u.name }))
  fetchList()
})

async function fetchList() {
  loading.value = true
  try {
    const params: any = {}
    if (query.keyword) params.keyword = query.keyword
    if (query.user_id) params.user_id = query.user_id
    if (query.result) params.result = query.result
    params.page = query.page
    params.page_size = query.page_size
    const res = await auditApi.list(params)
    items.value = res.data?.items ?? []
    total.value = res.data?.total ?? 0
  } finally {
    loading.value = false
  }
}

function onSearch() {
  query.page = 1
  fetchList()
}

const mobileFilterOpen = ref(false)
const mobileFilter = reactive({ keyword: '', user_id: undefined as number | undefined, result: undefined as string | undefined })

const activeFilterCount = computed(() => {
  let n = 0
  if (query.keyword) n++
  if (query.user_id != null) n++
  if (query.result) n++
  return n
})

function openMobileFilter() {
  mobileFilter.keyword = query.keyword
  mobileFilter.user_id = query.user_id
  mobileFilter.result = query.result
  mobileFilterOpen.value = true
}

function applyMobileFilter() {
  query.keyword = mobileFilter.keyword
  query.user_id = mobileFilter.user_id
  query.result = mobileFilter.result
  mobileFilterOpen.value = false
  onSearch()
}

function resetMobileFilter() {
  mobileFilter.keyword = ''
  mobileFilter.user_id = undefined
  mobileFilter.result = undefined
}
</script>

<template>
  <div :style="{ padding: isMobile ? '12px 8px' : '24px' }">
    <a-card :body-style="{ padding: isMobile ? '12px' : '16px 24px 24px' }" style="border-radius:12px;box-shadow:0 2px 12px rgba(0,0,0,.06);border:none">
    <div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:12px;align-items:center;margin-bottom:16px">
      <a-form v-if="!isMobile" layout="inline">
        <a-form-item label="关键词">
          <a-input v-model:value="query.keyword" placeholder="操作人/操作/对象/IP" allow-clear style="width:200px"
            @change="onSearch" />
        </a-form-item>
        <a-form-item label="操作人">
          <a-select v-model:value="query.user_id" placeholder="全部" allow-clear style="width:120px" @change="onSearch">
            <a-select-option v-for="u in userOptions" :key="u.id" :value="u.id">{{ u.full_name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="结果">
          <a-select v-model:value="query.result" placeholder="全部" allow-clear style="width:90px" @change="onSearch">
            <a-select-option value="success">成功</a-select-option>
            <a-select-option value="failure">失败</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item>
          <a-button @click="() => { query.keyword = ''; query.user_id = undefined; query.result = undefined; onSearch() }">重置</a-button>
        </a-form-item>
      </a-form>
      <a-badge v-if="isMobile" :count="activeFilterCount" :offset="[-2, 2]">
        <a-button @click="openMobileFilter"><template #icon><filter-outlined /></template>筛选</a-button>
      </a-badge>
    </div>

    <!-- 移动端卡片 -->
    <template v-if="isMobile">
      <a-spin :spinning="loading">
        <a-list :data-source="items" :locale="{ emptyText: '暂无数据' }">
          <template #renderItem="{ item: record }">
            <a-list-item style="padding:0;margin-bottom:10px;display:block">
              <a-card size="small" style="border-radius:8px;border:1px solid #f0f0f0">
                <div style="display:flex;justify-content:space-between;align-items:flex-start">
                  <div>
                    <div style="font-weight:600;color:#111827;font-size:13px">{{ record.action }}</div>
                    <div style="font-size:13px;color:#6b7280;margin-top:2px">操作人：{{ record.user_name }}</div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:2px">对象：{{ record.resource }}</div>
                    <div style="font-size:12px;color:#9ca3af;margin-top:2px">时间：{{ record.created_at?.slice(0, 19).replace('T', ' ') }}</div>
                  </div>
                  <a-tag :color="RESULT_COLOR[record.result]" style="margin:0">{{ RESULT_LABEL[record.result] }}</a-tag>
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
    <a-table v-else
      :columns="columns"
      :data-source="items"
      :loading="loading"
      :scroll="{ x: 1050 }"
      row-key="id"
      size="middle"
      :pagination="{
        total,
        current: query.page,
        pageSize: query.page_size,
        showTotal: (t: number) => `共 ${t} 条`,
        onChange: (p: number) => { query.page = p; fetchList() },
      }"
    >
      <template #bodyCell="{ column, record, index }">
        <template v-if="column.key === '_seq'">{{ (query.page - 1) * query.page_size + index + 1 }}</template>
        <template v-else-if="column.key === 'result'">
          <a-tag :color="RESULT_COLOR[record.result]">{{ RESULT_LABEL[record.result] }}</a-tag>
        </template>
      </template>
    </a-table>
    </a-card>

    <!-- 移动端筛选抽屉 -->
    <a-drawer v-if="isMobile" title="筛选" placement="bottom" height="55vh" :open="mobileFilterOpen" @close="mobileFilterOpen = false">
      <a-form layout="vertical">
        <a-form-item label="关键词"><a-input v-model:value="mobileFilter.keyword" placeholder="操作人/操作/对象/IP" allow-clear /></a-form-item>
        <a-form-item label="操作人">
          <a-select v-model:value="mobileFilter.user_id" placeholder="全部" allow-clear style="width:100%">
            <a-select-option v-for="u in userOptions" :key="u.id" :value="u.id">{{ u.full_name }}</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="结果">
          <a-select v-model:value="mobileFilter.result" placeholder="全部" allow-clear style="width:100%">
            <a-select-option value="success">成功</a-select-option>
            <a-select-option value="failure">失败</a-select-option>
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
  </div>
</template>
