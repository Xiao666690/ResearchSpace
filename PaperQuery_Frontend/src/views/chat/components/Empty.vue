<script setup lang="ts">
import { Compass, FileText, MessageSquare, Quote } from 'lucide-vue-next'
</script>
<template>
  <section class="chat-empty">
    <div class="conversation-orbit" aria-hidden="true">
      <i /><i /><span><Compass :size="32" :stroke-width="1.2" /></span><b />
    </div>
    <p class="chat-kicker">DIALOGUE / DISCOVERY</p>
    <h2>好问题，打开新的视野。</h2>
    <p>从一个问题开始。绑定论文后，让回答与原文证据保持连接。</p>
    <div class="conversation-guide">
      <span><FileText :size="15" />绑定研究论文</span
      ><span><MessageSquare :size="15" />追问与比较</span
      ><span><Quote :size="15" />核对原文引用</span>
    </div>
  </section>
</template>
<style scoped>
.chat-empty {
  min-height: 400px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 30px 16px;
  color: var(--rs-ink);
}
.conversation-orbit {
  width: 126px;
  height: 126px;
  position: relative;
  display: grid;
  place-items: center;
  margin-bottom: 26px;
}
.conversation-orbit i {
  position: absolute;
  inset: 5px;
  border: 1px solid #e5e1f0;
  border-radius: 50%;
  transform: rotate(-25deg) scaleY(0.75);
}
.conversation-orbit i:nth-child(2) {
  inset: 18px;
  transform: rotate(35deg) scaleY(0.75);
}
.conversation-orbit span {
  display: grid;
  place-items: center;
  height: 58px;
  width: 58px;
  border: 1px solid #e4dff0;
  border-radius: 18px;
  color: var(--rs-primary);
  background: #f1eef9;
}
.conversation-orbit b {
  position: absolute;
  width: 7px;
  height: 7px;
  background: #b58c53;
  border-radius: 50%;
  right: 10px;
  top: 44px;
}
.chat-kicker {
  font-size: 10px !important;
  letter-spacing: 0.18em;
  color: var(--rs-primary) !important;
}
.chat-empty h2 {
  font-size: clamp(23px, 3vw, 32px);
  letter-spacing: -0.04em;
  font-weight: 500;
  margin: 10px 0 14px;
}
.chat-empty > p {
  font-size: 13px;
  color: var(--rs-muted);
  max-width: 420px;
  line-height: 1.9;
}
.conversation-guide {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 26px;
  color: var(--rs-muted);
  font-size: 11px;
}
.conversation-guide span {
  display: flex;
  gap: 6px;
  align-items: center;
}
@media (max-width: 600px) {
  .chat-empty {
    min-height: 320px;
  }
  .conversation-guide {
    gap: 12px;
  }
  .conversation-orbit {
    width: 100px;
    height: 100px;
  }
}
</style>
