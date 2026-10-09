<!-- 这是一个输入框 -->
<template>
  <div class="composer-box flex p-3 space-x-2 w-1/2 items-end m-auto">
    <FileUploader />
    <el-input
      id="input_1"
      v-model="input"
      class="textarea"
      type="textarea"
      :autosize="{ minRows: 1, maxRows: 8 }"
      placeholder="提出一个问题，或继续探索刚才的发现…"
      aria-label="输入研究问题"
      resize="none"
      @keydown.enter.prevent="handleButtonClick"
    />
    <div>
      <el-button
        aria-label="发送问题"
        :disabled="!input.trim()"
        @click="handleButtonClick"
      >
        <IconoirProvider
          :icon-props="{
            color: '#ffffff',
            'stroke-width': 1,
            width: '2em',
            height: '2em',
          }"
        >
          <SendSolid />
        </IconoirProvider>
      </el-button>
    </div>
  </div>
</template>

<style lang="less" scoped>
@focus-border-color: #000000;

.el-button {
  border-radius: 10px;
  background-color: #e8e1ff;
  --el-button-hover-border-color: #ded9ee;
  --el-button-border-color: #e5e1f0;
  --el-button-disabled-border-color: transparent;
  --el-button-disabled-bg-color: none;
  --el-button-active-border-color: #cec7e5;
}
.composer-box :deep(.el-button:hover) {
  background: #d5c9ff;
}

.composer-box {
  border: 1px solid #e3e3e6;
  border-radius: 18px;
  background: #fff;
  box-shadow: 0 7px 24px rgba(32, 32, 36, 0.07);
  transition:
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}
.composer-box:focus-within {
  border-color: #cfc8e7;
  box-shadow:
    0 8px 28px rgba(74, 62, 137, 0.1),
    0 0 0 3px rgba(109, 91, 208, 0.07);
}

.el-textarea {
  font-family:
    ui-sans-serif,
    -apple-system,
    system-ui,
    Segoe UI,
    Roboto,
    Ubuntu,
    Cantarell,
    Noto Sans,
    sans-serif,
    Helvetica,
    Apple Color Emoji,
    Arial,
    Segoe UI Emoji,
    Segoe UI Symbol;
  font-size: 1rem;
  --el-input-focus-border-color: none;
  --el-input-bg-color: none;
  --el-input-border-color: none;
  --el-input-hover-border-color: none;
}
.composer-box {
  width: min(760px, calc(100% - 32px));
  border-radius: 14px;
  padding: 12px;
  box-shadow: 0 5px 24px #24202c0a;
}
.composer-box .el-button {
  height: 38px;
  width: 38px;
  padding: 7px;
  border: 0;
  background: var(--rs-primary);
  border-radius: 9px;
}
.composer-box :deep(.el-button:hover) {
  background: #594ac2;
}
.composer-box :deep(.el-textarea__inner) {
  padding: 7px 10px;
  line-height: 1.7;
  box-shadow: none !important;
  background: transparent;
  font-size: 14px;
}
.composer-box .el-button.is-disabled {
  background: #dfdce9;
  color: #aaa;
}
.composer-box :deep(.el-button svg) {
  height: 20px;
  width: 20px;
}
@media (max-width: 600px) {
  .composer-box {
    width: calc(100% - 20px);
    padding: 8px;
  }
}
</style>

<script setup lang="ts">
import { IconoirProvider, SendSolid } from '@iconoir/vue'

import { ref, nextTick } from 'vue'

import { useMessageListStore } from '@/stores/messageList'

import FileUploader from './DocumentUploader.vue'

const input = ref('')

// 在这里处理按钮点击事件 向gpt发送问题
const handleButtonClick = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && e.shiftKey) {
    input.value += '\n'
    const textarea = document.getElementById('input_1')
    nextTick(() => {
      if (!textarea) return
      textarea.scrollTop = textarea.scrollHeight
    })
    return
  }
  if (!input.value) {
    return
  }
  const question = input.value
  input.value = ''
  const messageList = useMessageListStore()
  messageList.addUserMessage({
    role: 'user',
    content: question,
  })
}
</script>
