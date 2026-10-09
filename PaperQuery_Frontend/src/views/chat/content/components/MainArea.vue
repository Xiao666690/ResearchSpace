<!-- 这是内容区域的中部 用于显示对话列表 -->
<template>
  <div
    ref="messageContainer"
    class="chat-message-stream flex justify-center overflow-y-auto p-8 mb-14"
  >
    <div class="w-full max-w-4xl">
      <Empty v-show="messageList.length === 0" />
      <div v-for="message in messageList" :key="message.id" class="mb-10">
        <MessageBox
          :role="message.role"
          :content="message.content"
          :model-label="message.modelLabel"
          :citations="message.citations"
          :external-papers="message.externalPapers"
          :search-status="message.searchStatus"
          :search-state="message.searchState"
          :search-steps="message.searchSteps"
          :status="message.status"
          :started-at="message.createdAt"
          :thinking-ms="message.thinkingMs"
          :duration-ms="message.durationMs"
          :documents="message.documents"
          @save-evidence="saveEvidence(message)"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import MessageBox from '../../components/MessageBox.vue'
import Empty from '../../components/Empty.vue'
import { useMessageListStore } from '@/stores/messageList'
import { ref, computed, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { addClaimCitation, createClaim } from '@/api/evidence'
import type { Message } from '@/stores/messageList'

const route = useRoute()
async function saveEvidence(message: Message) {
  const projectId = String(route.params.projectId || '')
  if (!projectId || !message.citations?.length) return
  try {
    const { value } = await ElMessageBox.prompt(
      '为这条研究观点命名',
      '保存到证据看板',
      {
        inputValue: message.content.replace(/\[C\d+\]/g, '').slice(0, 60),
        inputValidator: (input) => !!input.trim() || '请输入标题',
      },
    )
    const claim = await createClaim(projectId, value.trim(), message.content)
    let saved = 0
    for (const citation of message.citations) {
      if (!citation.knowledgeID) continue
      try {
        await addClaimCitation(projectId, claim.claim_id, citation)
        saved++
      } catch {
        /* remaining citations still save */
      }
    }
    ElMessage.success(
      saved
        ? `已保存观点及 ${saved} 条原文证据`
        : '已保存观点，但引用未能通过原文核验',
    )
  } catch (error: any) {
    if (error !== 'cancel' && error !== 'close')
      ElMessage.error(error?.response?.data?.detail || '保存失败')
  }
}

const store = useMessageListStore()

const messageContainer = ref<HTMLElement | null>(null)

const messageList = computed(() => {
  return store.state.messageList
})

// 监听消息变化并自动滚动到底部
watch(store.state.messageList, (newValue) => {
  if (newValue) {
    scrollToBottom()
  }
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messageContainer.value) {
      messageContainer.value.scrollTop = messageContainer.value.scrollHeight
    }
  })
}
</script>

<style scoped>
.chat-message-stream {
  padding: 28px 24px 100px;
}
@media (max-width: 600px) {
  .chat-message-stream {
    padding: 16px 12px 100px;
  }
}
</style>
