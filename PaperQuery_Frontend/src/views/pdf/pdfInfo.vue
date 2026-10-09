<template>
  <div class="reader-workspace" :class="`mobile-${mobilePanel}`">
    <header class="workspace-bar"><button type="button" @click="router.push('/home/library')">← 论文库</button><div><span class="workspace-kicker">READING ROOM</span><strong>阅读与思考</strong></div><span class="reading-indicator"><i :class="{ ready: readerReady }" />{{ readerReady ? '在前台阅读时记录时长' : '正在准备论文' }}</span></header><div class="mobile-reader-tabs" aria-label="阅读工具"><button :aria-pressed="mobilePanel === 'paper'" @click="mobilePanel = 'paper'">论文</button><button :aria-pressed="mobilePanel === 'tools'" @click="mobilePanel = 'tools'">翻译、笔记与问答</button></div>
    <ResizablePanelGroup id="group_1" direction="horizontal" class="w-full h-full reader-panels">
      <ResizablePanel id="panel-1" :default-size="64" :min-size="0" :collapsed-size="0" collapsible class="h-full min-w-0 paper-panel">
        <div class="w-full h-full">
          <pdfViewer :key="`${knowledgeID}:${documentID}`" :knowledge-i-d="knowledgeID" :document-i-d="documentID" @selection="onSelection" @loaded="readerReady = true" />
        </div>
      </ResizablePanel>
      <ResizableHandle with-handle class="reader-handle" />
      <ResizablePanel id="panel-2" :default-size="36" :min-size="0" :collapsed-size="0" collapsible class="h-full min-w-0 tools-panel">
        <div class="flex flex-col w-full h-full min-w-0 overflow-hidden">
          <ResizablePanelGroup id="group_2" direction="vertical" class="h-full min-w-0 w-full">
            <ResizablePanel id="panel-2-1" :default-size="50" :min-size="0" :collapsed-size="0" collapsible class="h-full min-h-0">
              <div class="flex flex-1 h-full min-w-0 overflow-hidden">
                <translateBox :key="`${knowledgeID}:${documentID}`" :knowledge-id="knowledgeID" :document-id="documentID" />
              </div>
            </ResizablePanel>
            <ResizableHandle with-handle class="reader-handle" />
            <ResizablePanel id="panel-2-2" :default-size="50" :min-size="0" :collapsed-size="0" collapsible class="h-full min-h-0">
              <div class="flex flex-1 h-full min-w-0 overflow-hidden">
                <chat :key="`${knowledgeID}:${documentID}`" class="flex-1" :knowledge-id="knowledgeID" :document-id="documentID" :selected-text="selectedText" :selected-page="selectedPage" @clear-selection="selectedText = ''" />
              </div>
            </ResizablePanel>
          </ResizablePanelGroup>
        </div>
      </ResizablePanel>
    </ResizablePanelGroup>
  </div>
</template>

<style scoped>
.reader-workspace { display: flex; flex-direction: column; flex: 1 1 0%; width: 100%; height: 100%; min-width: 0; min-height: 0; overflow: clip; }
.reader-handle { z-index: 10; background: #d4d9e5; transition: background-color .18s ease, box-shadow .18s ease; }
.reader-handle:hover, .reader-handle:focus-visible { background: #6756c5; box-shadow: 0 0 0 3px rgba(103,86,197,.16); }
.reader-handle :deep(div) { width: 18px; height: 24px; color: #5548ad; background: #fff; border: 1px solid #a9a1d6; }
.workspace-bar{display:flex;align-items:center;gap:20px;flex:none;min-height:60px;padding:10px 18px;background:#fff;border-bottom:1px solid var(--rs-border,#E5E7EB)}.workspace-bar>button{font-size:12px;padding:7px 10px;border-radius:8px;background:#F5F3FA;color:var(--rs-primary,#6858D6);transition:transform 120ms var(--rs-ease,cubic-bezier(.23,1,.32,1))}.workspace-bar>button:active{transform:scale(.98)}.workspace-bar>button:focus-visible{outline:2px solid #6858D6;outline-offset:2px}.workspace-bar>div{display:flex;align-items:center;gap:10px}.workspace-kicker{font-size:9px;letter-spacing:.14em;color:#94959A}.workspace-bar strong{font-size:13px;font-weight:500}.reading-indicator{display:flex;align-items:center;gap:7px;margin-left:auto;color:#7D827E;font-size:10px}.reading-indicator i{width:5px;height:5px;border-radius:50%;background:#AEB2B5}.reading-indicator i.ready{background:#71987D}.reader-panels{flex:1;min-height:0}.reader-handle{background:#E5E4DF}.reader-handle :deep(div){border-color:#DEDAEB;border-radius:5px}.reader-workspace :deep(.paper-chat){border:0}.reader-workspace :deep(.chat-header){background:#FCFBF8}.reader-workspace :deep(.chat-composer button){background:var(--rs-primary,#6858D6)}@media(max-width:680px){.workspace-bar{gap:8px;padding:8px}.workspace-kicker,.reading-indicator{display:none}}@media(prefers-reduced-motion:reduce){.workspace-bar>button{transition:none}.workspace-bar>button:active{transform:none}}
.reader-workspace{height:calc(100dvh - 64px)}.mobile-reader-tabs{display:none}@media(max-width:680px){.reader-workspace{height:calc(100dvh - 58px)}.mobile-reader-tabs{display:flex;gap:6px;padding:8px;background:white;border-bottom:1px solid var(--rs-line)}.mobile-reader-tabs button{padding:8px 12px;border-radius:8px;font-size:12px;color:var(--rs-muted)}.mobile-reader-tabs button[aria-pressed=true]{background:var(--rs-primary-soft);color:var(--rs-primary)}.reader-panels{height:calc(100dvh - 165px);min-height:420px;flex:none}.mobile-paper .tools-panel,.mobile-tools .paper-panel,.reader-panels>.reader-handle{display:none!important}.mobile-paper .paper-panel,.mobile-tools .tools-panel{flex:1 1 100%!important}}
.reader-workspace .reader-panels{flex:1!important;height:0!important;min-height:0}</style>

<script setup lang="ts">
import pdfViewer from '@/views/pdf/pdfViewer.vue'
import chat from '@/views/smallChat/chat.vue'
import translateBox from '@/views/translate/translateBox.vue'
import { useRoute, useRouter } from 'vue-router'
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
const selectedText = ref('')
const selectedPage = ref(1)
const readerReady = ref(false)
const mobilePanel = ref(route.query.tab === 'note' ? 'tools' : 'paper')
const isMobile = useMediaQuery('(max-width: 680px)')
const trackingReady = computed(() => readerReady.value && (!isMobile.value || mobilePanel.value === 'paper'))
const onSelection = (text: string, page: number) => {
  selectedText.value = text
  selectedPage.value = page
}

watch([knowledgeID, documentID], () => { readerReady.value = false }, { flush: 'sync' })
useReadingTracker(knowledgeID, documentID, trackingReady)
watch([knowledgeID, documentID], () => { selectedText.value = ''; selectedPage.value = 1 })
</script>
