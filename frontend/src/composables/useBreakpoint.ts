import { computed } from 'vue'
import { Grid } from 'ant-design-vue'

export function useBreakpoint() {
  const screens = Grid.useBreakpoint()
  const isMobile = computed(() => !screens.value.md)
  return { isMobile, screens }
}
