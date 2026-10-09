<template>
  <div class="chat-workspace">
    <div class="mobile-chat-toolbar">
      <button
        class="rs-button rs-control-outline"
        type="button"
        @click="historyOpen = true"
      >
        <History :size="15" />历史会话
      </button>
    </div>
    <ResizablePanelGroup
      direction="horizontal"
      class="h-full w-full chat-panels"
    >
      <ResizablePanel
        :default-size="76"
        :min-size="45"
        class="min-w-0 chat-main-panel"
        ><Content class="h-full min-w-0"
      /></ResizablePanel>
      <ResizableHandle with-handle class="chat-handle" />
      <ResizablePanel
        :default-size="24"
        :min-size="0"
        :collapsed-size="0"
        collapsible
        class="min-w-0 chat-history-panel"
        ><SideBar class="h-full"
      /></ResizablePanel>
    </ResizablePanelGroup>
    <el-drawer
      v-model="historyOpen"
      title="历史会话"
      size="min(360px, calc(100vw - 32px))"
      append-to-body
      class="history-drawer"
      ><SideBar
    /></el-drawer>
  </div>
</template>

<style scoped>
.chat-workspace {
  display: flex;
  height: 100vh;
  min-width: 0;
  overflow: hidden;
}
.chat-handle {
  z-index: 10;
  background: #d8d8df;
  transition: background-color 0.18s ease;
}
.chat-handle:hover,
.chat-handle:focus-visible {
  background: #6d5bd0;
}
.chat-workspace {
  position: relative;
  flex-direction: column;
}
.mobile-chat-toolbar {
  display: none;
}
.chat-panels {
  flex: 1;
  min-height: 0;
  height: 0 !important;
}
@media (max-width: 767px) {
  .mobile-chat-toolbar {
    display: flex;
    justify-content: flex-end;
    padding: 8px 14px;
    background: #fff;
    border-bottom: 1px solid var(--rs-line);
  }
  .mobile-chat-toolbar button {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 7px 10px;
    font-size: 12px;
  }
  .chat-history-panel,
  .chat-handle {
    display: none !important;
  }
  .chat-main-panel {
    flex: 1 1 100% !important;
  }
}
</style>

<script setup lang="ts">
import Content from './content/ContentView.vue'
import SideBar from './sidebar/SideBar.vue'
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@/components/ui/resizable'
import { onMounted, ref } from 'vue'
import { History } from 'lucide-vue-next'
const historyOpen = ref(false)
import { useRoute } from 'vue-router'
import { useMessageListStore } from '@/stores/messageList'
import { useChatHistoryStore } from '@/stores/chatHistory'

const route = useRoute()
onMounted(() => {
  const history = useChatHistoryStore()
  const scope =
    typeof route.params.projectId === 'string'
      ? route.params.projectId
      : 'workspace'
  if (history.state.activeScope !== scope) {
    // Preserve the current conversation when returning to the same scope.
    useMessageListStore().clearMessages()
    history.loadFromStorage()
    history.state.activeScope = scope
  }
})
</script>
