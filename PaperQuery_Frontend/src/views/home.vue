<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { DialogRoot, DialogPortal, DialogOverlay, DialogContent, DialogTitle, DialogDescription, DialogClose } from 'radix-vue'
import { X } from 'lucide-vue-next'
import SideBar from '@/components/SideBar.vue'
import WorkspaceHeader from '@/components/WorkspaceHeader.vue'
const isCollapsed=ref(false), mobileOpen=ref(false)
const workspaceHeader=ref<InstanceType<typeof WorkspaceHeader>|null>(null)
const route=useRoute()
watch(()=>route.path,()=>{mobileOpen.value=false})
function search(){mobileOpen.value=false;workspaceHeader.value?.openSearch()}
</script>
<template>
  <div id="home" class="app-shell">
    <div class="desktop-navigation"><SideBar :is-collapsed="isCollapsed" @toggle-collapse="isCollapsed=!isCollapsed" @search="search"/></div>
    <div class="workspace-stage"><WorkspaceHeader ref="workspaceHeader" @open-navigation="mobileOpen=true"/><router-view class="workspace-page"/></div>
    <DialogRoot v-model:open="mobileOpen"><DialogPortal><DialogOverlay class="navigation-overlay"/><DialogContent class="navigation-drawer"><DialogTitle class="sr-only">研究工作区导航</DialogTitle><DialogDescription class="sr-only">选择要打开的研究功能</DialogDescription><SideBar mobile @navigate="mobileOpen=false" @search="search"/><DialogClose class="navigation-close rs-button" aria-label="关闭导航"><X :size="18"/></DialogClose></DialogContent></DialogPortal></DialogRoot>
  </div>
</template>
<style scoped>
.app-shell{display:flex;width:100%;min-width:0;min-height:100dvh;height:100dvh;background:var(--rs-canvas)}.desktop-navigation{flex:none}.workspace-stage{flex:1;min-width:0;width:0;height:100%;overflow-y:auto;overflow-x:hidden}.workspace-page{min-width:0}.navigation-overlay{position:fixed;inset:0;z-index:60;background:rgb(8 13 24 / .4);backdrop-filter:blur(3px)}.navigation-drawer{position:fixed;left:0;top:0;bottom:0;z-index:61;width:264px;background:var(--rs-surface);box-shadow:20px 0 60px rgb(0 0 0 / .12);outline:none}.navigation-close{position:absolute;top:24px;right:16px;width:30px;height:30px;border-radius:8px;display:grid;place-items:center;color:var(--rs-muted)}.navigation-drawer[data-state=open]{animation:nav-open 220ms var(--rs-ease)}.navigation-drawer[data-state=closed]{animation:nav-close 160ms var(--rs-ease)}.navigation-overlay[data-state=open]{animation:nav-fade 180ms ease}.navigation-close:hover{background:var(--rs-surface-soft)}
@keyframes nav-open{from{transform:translateX(-100%)}to{transform:translateX(0)}}@keyframes nav-close{to{transform:translateX(-100%)}}@keyframes nav-fade{from{opacity:0}to{opacity:1}}
@media(max-width:767px){.desktop-navigation{display:none}.workspace-stage{width:100%}}
@media(prefers-reduced-motion:reduce){.navigation-drawer,.navigation-overlay{animation:none!important}}
</style>