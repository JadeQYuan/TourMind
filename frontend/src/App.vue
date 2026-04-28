<script setup lang="ts">
import { theme } from 'ant-design-vue'

const { defaultAlgorithm } = theme

const themeConfig = {
  algorithm: defaultAlgorithm,
  token: {
    colorPrimary: '#0d9488',
    colorLink: '#0d9488',
    colorSuccess: '#10b981',
    colorWarning: '#f59e0b',
    colorError: '#ef4444',
    borderRadius: 8,
    fontFamily: "'PingFang SC', 'Microsoft YaHei', system-ui, sans-serif",
  },
  components: {
    Layout: {
      siderBg: '#f0fdf9',
      triggerBg: '#ccfbf1',
    },
    Menu: {
      itemBg: 'transparent',
      itemSelectedBg: '#e6f4f1',
      itemSelectedColor: '#0d9488',
      itemHoverBg: '#f0faf8',
      itemHoverColor: '#0d9488',
      itemColor: '#4b5563',
      itemBorderRadius: 8,
      itemMarginInline: 8,
    },
  },
}
</script>

<template>
  <a-config-provider :theme="themeConfig">
    <router-view />
  </a-config-provider>
</template>
