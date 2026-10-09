<script setup lang="ts">
import { computed, ref, watch, onBeforeUnmount } from 'vue'
const props = defineProps<{ minutes: number; papers: number }>()
const minutes = computed(() => Math.max(0, Number(props.minutes) || 0))
const fill = computed(() => Math.min(1, minutes.value / 60))
const settling = ref(false)
let timer: ReturnType<typeof setTimeout> | undefined
watch(minutes, (value, previous) => {
  if (value <= previous) return
  settling.value = true
  clearTimeout(timer)
  timer = setTimeout(() => { settling.value = false }, 1200)
})
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <section class="reading-vessel" :aria-label="`今日阅读 ${minutes} 分钟，研读 ${papers} 篇论文`">
    <div class="vessel-copy"><p class="vessel-eyebrow">TIME, WELL SPENT</p><h3>每一分钟，<br>都沉淀为新的理解。</h3><div class="vessel-number">{{ minutes }}<span>分钟</span></div><p class="vessel-detail">今日研读 {{ papers }} 篇论文</p><p class="vessel-footnote">沙瓶以 60 分钟为视觉刻度，累计时长不设上限。</p></div>
    <div class="vessel-art" aria-hidden="true">
      <svg viewBox="0 0 180 240" class="bottle" :class="{ settling }">
        <defs><clipPath id="reading-bottle-clip"><path d="M68 29H112V65Q112 78 126 90Q143 104 143 123V198Q143 214 127 214H53Q37 214 37 198V123Q37 104 54 90Q68 78 68 65Z" /></clipPath><linearGradient id="reading-sand" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#D8BA83"/><stop offset="1" stop-color="#B58C53"/></linearGradient></defs>
        <ellipse cx="90" cy="224" rx="58" ry="7" fill="#202124" opacity=".045" />
        <path d="M68 29H112V65Q112 78 126 90Q143 104 143 123V198Q143 214 127 214H53Q37 214 37 198V123Q37 104 54 90Q68 78 68 65Z" fill="#FFFFFF" fill-opacity=".5" stroke="#B8ADA0" stroke-width="1.5" />
        <g clip-path="url(#reading-bottle-clip)"><g class="sand-fill" :style="{ transform: `translateY(${(1 - fill) * 174}px)` }"><path d="M30 47Q59 38 90 47T150 47V218H30Z" fill="url(#reading-sand)"/><path d="M37 53Q75 44 110 54T143 53" fill="none" stroke="#F2DFC0" stroke-width="2" opacity=".7"/><circle v-for="grain in 24" :key="grain" :cx="42 + (grain * 17 % 94)" :cy="67 + (grain * 23 % 135)" r=".8" fill="#FAEBD0" opacity=".5" /></g><path class="sand-stream" d="M90 43V188" stroke="#C9A36A" stroke-width="2" stroke-dasharray="2 8" /></g>
        <path d="M63 21H117V31H63Z" fill="#B58C53"/><path d="M49 120V195Q49 202 55 202" stroke="#FFFFFF" stroke-width="4" opacity=".85" fill="none"/>
        <g stroke="#A9A09A" stroke-width="1"><path d="M150 55H158M150 95H155M150 135H158M150 175H155M150 214H158"/></g><g fill="#8C847C" font-size="9" font-family="sans-serif"><text x="161" y="58">60</text><text x="161" y="138">30</text><text x="161" y="217">0</text></g>
      </svg>
    </div>
  </section>
</template>

<style scoped>
.reading-vessel{display:flex;align-items:center;justify-content:space-between;gap:20px;min-height:274px;padding:28px 30px;background:linear-gradient(120deg,#FBFAF6,#F4F1E9);border:1px solid #E7E2D8;border-radius:16px;overflow:hidden}.vessel-copy{min-width:0}.vessel-eyebrow{font-size:10px;letter-spacing:.18em;color:#8C7048;font-weight:650}.vessel-copy h3{font-size:22px;line-height:1.55;letter-spacing:-.03em;margin:10px 0;color:var(--rs-ink,#202124);font-weight:500}.vessel-number{font-size:48px;line-height:1.2;letter-spacing:-.05em;font-variant-numeric:tabular-nums}.vessel-number span{font-size:12px;letter-spacing:0;color:var(--rs-muted,#687078);margin-left:10px}.vessel-detail{font-size:12px;color:var(--rs-muted,#687078);margin:8px 0}.vessel-footnote{font-size:10px;color:#847E75;max-width:250px;line-height:1.7}.vessel-art{flex:none;width:172px}.bottle{width:100%;overflow:visible}.sand-fill{transition:transform 1200ms var(--rs-ease,cubic-bezier(.23,1,.32,1))}.sand-stream{opacity:0}.settling .sand-stream{opacity:.65;animation:falling-grains 300ms linear 4}@keyframes falling-grains{to{stroke-dashoffset:-10}}@media(max-width:520px){.reading-vessel{padding:22px 18px;gap:8px}.vessel-copy h3{font-size:18px}.vessel-art{width:125px}.vessel-number{font-size:40px}}@media(prefers-reduced-motion:reduce){.sand-fill{transition:none}.sand-stream{animation:none!important;opacity:0!important}}
.bottle text{font-size:9px;font-family:inherit}</style>
