<template>
  <div class="note-fullscreen" :class="`mobile-${mobilePanel}`">
    <header class="fullscreen-bar">
      <button
        type="button"
        class="back-btn"

        title="返回论文阅读页"
        @click="goBack"

      >← 返回</button>
      <span class="bar-title">笔记全屏编辑</span>
    </header><div class="mobile-note-tabs" aria-label="编辑区切换"><button :aria-pressed="mobilePanel === 'paper'" @click="mobilePanel = 'paper'">论文</button><button :aria-pressed="mobilePanel === 'note'" @click="mobilePanel = 'note'">编辑笔记</button></div>
    <div class="fullscreen-body">
      <ResizablePanelGroup id="note_full_1" direction="horizontal" class="w-full h-full">
        <ResizablePanel id="note-full-panel-1" :default-size="55" :min-size="0" :collapsed-size="0" collapsible class="h-full min-w-0 paper-panel">
          <div class="w-full h-full">
            <pdfViewer :key="`${knowledgeID}:${documentID}`" :knowledge-i-d="knowledgeID" :document-i-d="documentID" @loaded="readerReady = true" />
          </div>
        </ResizablePanel>
        <ResizableHandle with-handle class="note-full-handle" />
        <ResizablePanel id="note-full-panel-2" :default-size="45" :min-size="0" :collapsed-size="0" collapsible class="h-full min-w-0 note-panel">
          <div class="note-paper">
            <note :key="`${knowledgeID}:${documentID}`" class="w-full h-full" :knowledgeID="knowledgeID" :documentID="documentID" :hide-fullscreen="true"></note>
          </div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </div>
  </div>
</template>

<style scoped>
.note-fullscreen { display: flex; flex-direction: column; width: 100%; height: 100vh; min-width: 0; min-height: 0; overflow: clip; }
/* 顶部返回栏 */
.fullscreen-bar { display: flex; align-items: center; gap: 12px; flex: none; height: 44px; padding: 0 14px; background: #f7f9ff; border-bottom: 1px solid #e3e0f0; }
.back-btn { display: inline-flex; align-items: center; gap: 4px; border: none; border-radius: 8px; padding: 5px 12px; font-size: 13px; background: rgba(109,91,208,.12); color: #5a4bbd; cursor: pointer; transition: background .15s ease; }
.back-btn:hover { background: rgba(109,91,208,.20); }
.bar-title { font-size: 13px; color: #64748b; }
.fullscreen-body { flex: 1 1 0%; min-height: 0; min-width: 0; }
.note-full-handle { z-index: 10; background: #d4d9e5; transition: background-color .18s ease, box-shadow .18s ease; }
.note-full-handle:hover, .note-full-handle:focus-visible { background: #6756c5; box-shadow: 0 0 0 3px rgba(103,86,197,.16); }
.note-full-handle :deep(div) { width: 18px; height: 24px; color: #5548ad; background: #fff; border: 1px solid #a9a1d6; }

/* 笔记区：无卡片/圆角/投影/留白，直接铺满右面板 */
.note-paper {
  position: relative;
  height: 100%;
  width: 100%;
  background: transparent;
  border-radius: 0;
  box-shadow: none;
  padding: 0;
  overflow: hidden;
}

.back-btn{transition:transform 120ms var(--rs-ease,cubic-bezier(.23,1,.32,1)),background-color 140ms ease}.back-btn:active{transform:scale(.98)}.back-btn:focus-visible{outline:2px solid #6858D6;outline-offset:3px}.fullscreen-bar{height:56px;background:#FBFAF7}.bar-title{letter-spacing:.03em}@media(prefers-reduced-motion:reduce){.back-btn{transition:none}.back-btn:active{transform:none}}
.note-fullscreen{height:calc(100dvh - 64px)}.mobile-note-tabs{display:none}@media(max-width:680px){.note-fullscreen{height:calc(100dvh - 58px)}.mobile-note-tabs{display:flex;gap:6px;padding:8px;background:white;border-bottom:1px solid var(--rs-line)}.mobile-note-tabs button{padding:8px 12px;border-radius:8px;font-size:12px;color:var(--rs-muted)}.mobile-note-tabs button[aria-pressed=true]{background:var(--rs-primary-soft);color:var(--rs-primary)}.mobile-paper .note-panel,.mobile-note .paper-panel,.note-full-handle{display:none!important}.mobile-paper .paper-panel,.mobile-note .note-panel{flex:1 1 100%!important}}
</style>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import pdfViewer from '@/views/pdf/pdfViewer.vue'
import note from '@/views/note/note.vue'
import { useMediaQuery } from '@vueuse/core'
import { useReadingTracker } from '@/composables/useReadingTracker'
import {
  ResizableHandle,
  ResizablePanel,
  ResizablePanelGroup,
} from '@/components/ui/resizable'

const route = useRoute()
const router = useRouter()
const knowledgeID = computed(() => String(route.params.knowledgeID || ''))
const documentID = computed(() => String(route.params.documentID || ''))
const goBack = () => {
  // 优先回退到来源页；无历史（如直接刷新进入）则回论文阅读页
  if (window.history.length > 1) router.back()
  else router.push({ name: 'pdfInfo', params: { knowledgeID: knowledgeID.value, documentID: documentID.value } })
}
const readerReady = ref(false)
const mobilePanel = ref('note')
const isMobile = useMediaQuery('(max-width:680px)')
const trackingReady = computed(() => readerReady.value && (!isMobile.value || mobilePanel.value === 'paper'))
watch([knowledgeID, documentID], () => { readerReady.value = false }, { flush: 'sync' })
useReadingTracker(knowledgeID, documentID, trackingReady)
</script>
