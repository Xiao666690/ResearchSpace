<template>
  <div id="home" class="app-shell flex min-h-screen">
    <SideBar
      :is-collapsed="isCollapsed"
      @toggle-collapse="isCollapsed = !isCollapsed"
    />
    <router-view class="min-w-0 flex-1" />
  </div>
</template>

<script setup lang="ts">
const isCollapsed = ref(false)
</script>

<style lang="less" scoped>
.app-shell {
  position: relative;
  isolation: isolate;
  width: 100%;
  min-width: 0;
  overflow-x: clip;
  background: #f8f9ff;
}
.app-shell::before {
  position: fixed;
  inset: 0;
  z-index: -1;
  pointer-events: none;
  background: url('/images/researchspace-internal-background.png') center / cover no-repeat;
  content: '';
}
@media (max-width: 560px) {
  .app-shell { padding-bottom: 68px; }
  .app-shell::before { background-position: 28% center; }
}
</style>
