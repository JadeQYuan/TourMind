<script setup lang="ts">
import { ref, onMounted } from 'vue'

const emit = defineEmits<{ signed: [data: string] }>()
const canvas = ref<HTMLCanvasElement | null>(null)
let drawing = false
let ctx: CanvasRenderingContext2D | null = null

onMounted(() => {
  const el = canvas.value!
  ctx = el.getContext('2d')!
  ctx.strokeStyle = '#000'
  ctx.lineWidth = 2
  ctx.lineCap = 'round'

  el.addEventListener('mousedown', start)
  el.addEventListener('mousemove', draw)
  el.addEventListener('mouseup', end)
  el.addEventListener('mouseleave', end)
  el.addEventListener('touchstart', (e) => { e.preventDefault(); start(e.touches[0] as any) }, { passive: false })
  el.addEventListener('touchmove', (e) => { e.preventDefault(); draw(e.touches[0] as any) }, { passive: false })
  el.addEventListener('touchend', end)
})

function getPos(e: MouseEvent) {
  const rect = canvas.value!.getBoundingClientRect()
  return { x: e.clientX - rect.left, y: e.clientY - rect.top }
}

function start(e: MouseEvent) { drawing = true; const p = getPos(e); ctx!.beginPath(); ctx!.moveTo(p.x, p.y) }
function draw(e: MouseEvent) { if (!drawing) return; const p = getPos(e); ctx!.lineTo(p.x, p.y); ctx!.stroke() }
function end() { drawing = false; emit('signed', canvas.value!.toDataURL('image/png')) }

function clear() {
  ctx!.clearRect(0, 0, canvas.value!.width, canvas.value!.height)
  emit('signed', '')
}
</script>

<template>
  <div>
    <canvas ref="canvas" width="640" height="200"
      style="border:1px solid #d9d9d9;border-radius:4px;cursor:crosshair;touch-action:none;width:100%;max-width:640px" />
    <div style="margin-top:8px">
      <a-button size="small" @click="clear">清除重签</a-button>
    </div>
  </div>
</template>
