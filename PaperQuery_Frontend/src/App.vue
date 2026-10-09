<template>
  <div id="main router" class="flex-grow min-w-0 h-full">
    <router-view :key="key" class="" />
  </div>
</template>

<script setup lang="ts">
import { isMobile, watchResize } from '@bassist/utils'
const route = useRoute()
const key = computed(() => String(route.matched[0]?.path || route.path))

watchResize(() => {
  document.body.className = `platform-${isMobile() ? 'mobile' : 'desktop'}`
})
</script>
