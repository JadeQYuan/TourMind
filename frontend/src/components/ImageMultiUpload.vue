<template>
  <a-upload
    :action="uploadUrl"
    list-type="picture-card"
    :multiple="true"
    :max-count="maxCount"
    :accept="accept"
    :file-list="fileList"
    :before-upload="beforeUpload"
    @change="onChange"
    @preview="onPreview"
    @remove="onRemove"
  >
    <div v-if="fileList.length < maxCount">
      <plus-outlined />
      <div>上传</div>
    </div>
  </a-upload>
  <a-modal v-model:visible="previewVisible" :footer="null">
    <img :src="previewImage" style="width: 100%" />
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { message, Upload, Modal } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'

const props = defineProps({
  modelValue: {
    type: Array as () => string[],
    default: () => []
  },
  maxCount: {
    type: Number,
    default: 20
  },
  maxSizeMB: {
    type: Number,
    default: 10
  },
  accept: {
    type: String,
    default: 'image/*'
  },
  uploadUrl: {
    type: String,
    default: '/api/v1/files/upload'
  },
  data: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:modelValue'])

const fileList = ref<Upload['fileList']>([])
const previewVisible = ref(false)
const previewImage = ref('')

watch(
  () => props.modelValue,
  (val) => {
    fileList.value = (val || []).map((url, idx) => ({
      uid: String(idx),
      name: `图片${idx + 1}`,
      status: 'done',
      url
    }))
  },
  { immediate: true }
)

function beforeUpload(file: File) {
  if (!file.type.startsWith('image/')) {
    message.error('仅支持图片格式')
    return false
  }
  if (file.size / 1024 / 1024 > props.maxSizeMB) {
    message.error(`单张图片不能超过${props.maxSizeMB}MB`)
    return false
  }
  return true
}

function onChange(info: any) {
  if (info.file.status === 'done') {
    const urls = info.fileList
      .filter((f: any) => f.status === 'done' && (f.url || f.response?.data?.file_url))
      .map((f: any) => f.url || f.response?.data?.file_url)
    emit('update:modelValue', urls)
  } else if (info.file.status === 'removed') {
    const urls = info.fileList
      .filter((f: any) => f.status === 'done' && (f.url || f.response?.data?.file_url))
      .map((f: any) => f.url || f.response?.data?.file_url)
    emit('update:modelValue', urls)
  }
}

function onPreview(file: any) {
  previewImage.value = file.url || file.thumbUrl
  previewVisible.value = true
}

function onRemove(file: any) {
  // nothing special, handled in onChange
}
</script>

<style scoped>
.a-upload-list-picture-card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
</style>
