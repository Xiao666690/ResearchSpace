<!-- 这是底部的输入区域 -->
<template>
  <div class="relative flex w-full justify-center mt-4 mb-4">
    <div class="w-full relative flex">
      <div class="absolute bottom-0 w-full">
        <DocumentList class="chat-document-strip resize-none m-auto" />
        <InputBox class="w-1/2 resize-none m-auto"></InputBox>
      </div>
    </div>
  </div>
</template>

<style scoped>
.chat-document-strip {
  width: min(760px, calc(100% - 32px));
  margin-bottom: 8px;
}
@media (max-width: 600px) {
  .chat-document-strip {
    width: calc(100% - 20px);
  }
}
</style>

<script setup lang="ts">
import DocumentList from '../../components/DocumentList.vue'
import InputBox from '../../components/InputBox.vue'
</script>
