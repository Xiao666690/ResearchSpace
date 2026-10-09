<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { getSidebarGroups } from './utils/sidebar'
import { PanelLeftClose, PanelLeftOpen, Search, CircleCheck, CircleAlert } from 'lucide-vue-next'
import axios from 'axios'
const props = defineProps<{ isCollapsed?: boolean; mobile?: boolean }>()
const emit = defineEmits<{ (e:'toggleCollapse'):void; (e:'search'):void; (e:'navigate'):void }>()
const route = useRoute()
const projectId = computed(() => typeof route.params.projectId === 'string' ? route.params.projectId : null)
const role = ref(localStorage.getItem('role') || '')
const username = localStorage.getItem('username') || '研究者'
const sidebarGroups = computed(() => getSidebarGroups(role.value, projectId.value))
const status = ref<'checking'|'ready'|'unavailable'>('checking')
let healthTimer: ReturnType<typeof setInterval> | undefined
let disposed = false
const isActive = (link:string) => {
  const path=route.path.toLowerCase(),target=link.toLowerCase()
  return path===target || (target==='/home/library' && (path.startsWith('/home/knowledge/') || path.startsWith('/home/pdfinfo/')))
}
async function checkHealth() {
  if (document.hidden) return
  try { const {data}=await axios.get(`${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'}/health/ready`,{timeout:6000}); if(!disposed) status.value=data.status==='ready'?'ready':'unavailable' }
  catch { if(!disposed) status.value='unavailable' }
}
onMounted(async()=> {
  checkHealth(); healthTimer=setInterval(checkHealth,60000)
  if(role.value) return
  const token=localStorage.getItem('token'); if(!token) return
  try {
    const {data}=await axios.get(`${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8001'}/user/me`,{headers:{Authorization:`Bearer ${token}`},timeout:10000})
    if(data?.data?.role && !disposed) { role.value=data.data.role; localStorage.setItem('role',data.data.role); if(data.data.workspace_lid) localStorage.setItem('workspaceLid',data.data.workspace_lid) }
  } catch { /* Existing role fallback stays usable. */ }
})
onBeforeUnmount(()=>{ disposed=true; clearInterval(healthTimer) })
</script>
<template>
  <nav class="app-sidebar" :class="{collapsed:props.isCollapsed && !mobile,'mobile-sidebar':mobile}" aria-label="研究工作区导航">
    <div class="sidebar-topbar">
      <router-link to="/home/dashboard" class="brand" aria-label="研境首页" @click="emit('navigate')"><span class="brand-mark"><img src="/brand/researchspace-light.svg" alt="" width="30" height="30"/></span><span class="brand-copy"><strong>研境</strong><small>ResearchSpace</small></span></router-link>
      <button v-if="!mobile" type="button" class="collapse-toggle rs-button" :aria-label="isCollapsed?'展开侧边栏':'收起侧边栏'" :title="isCollapsed?'展开导航':'收起导航'" @click="emit('toggleCollapse')"><PanelLeftOpen v-if="isCollapsed" :size="16"/><PanelLeftClose v-else :size="16"/></button>
    </div>
    <button class="sidebar-search rs-button" type="button" title="查找功能" @click="emit('search')"><Search :size="16"/><span>查找功能</span><kbd>⌘ K</kbd></button>
    <div class="workspace-id"><span class="workspace-sigil">R</span><span><strong>我的研究空间</strong><small>{{ projectId?'项目研究中':'个人工作区' }}</small></span></div>
    <div class="nav-scroll"><section v-for="group in sidebarGroups" :key="group.title" class="nav-group"><h2 class="nav-label">{{ group.title }}</h2><div class="nav-list"><router-link v-for="item in group.items" :key="item.link" :to="item.link" class="nav-item" :class="{active:isActive(item.link)}" :aria-current="isActive(item.link)?'page':undefined" :aria-label="item.title" :title="isCollapsed?item.title:undefined" @click="emit('navigate')"><component :is="item.icon" :size="18"/><span>{{ item.title }}</span><i v-if="isActive(item.link)" class="active-pin"/></router-link></div></section></div>
    <div class="sidebar-footer"><div class="user-initial">{{ username.slice(0,1).toUpperCase() }}</div><div class="user-copy"><strong>{{ username }}</strong><small>{{ role==='admin'?'管理员':'研究者' }}</small></div></div>
    <button type="button" class="service-status" :class="status" :title="status==='ready'?'健康检查已通过':'点击重新检查服务'" @click="checkHealth"><CircleCheck v-if="status==='ready'" :size="13"/><CircleAlert v-else :size="13"/><span>{{ status==='ready'?'工作区已就绪':status==='checking'?'正在检查服务':'服务暂不可用' }}</span></button>
  </nav>
</template>
<style scoped>
.app-sidebar{position:sticky;top:0;flex:0 0 232px;width:232px;height:100dvh;display:flex;flex-direction:column;padding:24px 14px 16px;border-right:1px solid var(--rs-line);background:var(--rs-surface);color:var(--rs-ink);overflow:hidden}
.sidebar-topbar{display:flex;align-items:center;justify-content:space-between;margin:0 5px 25px;gap:8px}.brand{display:flex;align-items:center;gap:11px;text-decoration:none;color:inherit}.brand-mark{width:36px;height:36px;display:grid;place-items:center;background:var(--rs-primary-soft);color:var(--rs-primary);border-radius:11px}.brand-copy strong{font-size:19px;letter-spacing:.06em}.brand-copy small{display:block;font-size:9px;letter-spacing:.06em;color:var(--rs-muted);margin-top:1px}.collapse-toggle{height:28px;width:28px;display:grid;place-items:center;color:var(--rs-muted);border-radius:7px;flex:none}.sidebar-search{display:flex;align-items:center;gap:9px;width:100%;height:36px;padding:0 10px;border:1px solid var(--rs-line);border-radius:8px;color:var(--rs-muted);font-size:12px;background:var(--rs-canvas)}.sidebar-search kbd{margin-left:auto;font-size:9px;color:var(--rs-muted);border:1px solid var(--rs-line);padding:1px 4px;border-radius:4px}.workspace-id{display:flex;gap:10px;align-items:center;padding:20px 9px 14px}.workspace-sigil{width:28px;height:28px;display:grid;place-items:center;border:1px solid var(--rs-line);border-radius:7px;color:var(--rs-gold);font-family:Georgia,serif;background:var(--rs-canvas)}.workspace-id strong{font-size:11px;font-weight:600}.workspace-id small{display:block;color:var(--rs-muted);font-size:10px;margin-top:2px}.nav-scroll{flex:1;min-height:0;overflow:auto;padding-top:4px}.nav-group{margin:7px 0 15px}.nav-label{font-size:10px;color:var(--rs-muted);font-weight:500;margin:0 10px 6px;letter-spacing:.03em}.nav-list{display:flex;flex-direction:column;gap:3px}.nav-item{position:relative;display:flex;align-items:center;gap:11px;min-height:39px;padding:8px 10px;border-radius:8px;color:#666970;font-size:12px;text-decoration:none;transition:background-color 140ms ease,color 140ms ease}.nav-item svg{flex:none;opacity:.85}.nav-item.active{color:var(--rs-primary);background:var(--rs-primary-soft);font-weight:600}.nav-item.active svg{opacity:1}.active-pin{margin-left:auto;width:4px;height:4px;border-radius:50%;background:var(--rs-primary)}.sidebar-footer{display:flex;align-items:center;gap:10px;border-top:1px solid var(--rs-line);padding:17px 6px 9px}.user-initial{width:31px;height:31px;border-radius:50%;background:var(--rs-surface-soft);display:grid;place-items:center;color:var(--rs-primary);font-size:12px;border:1px solid var(--rs-line)}.user-copy{min-width:0}.user-copy strong{display:block;font-size:11px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:150px}.user-copy small{font-size:10px;color:var(--rs-muted)}.service-status{display:flex;align-items:center;gap:7px;margin:4px 10px 0;color:var(--rs-muted);font-size:10px;text-align:left}.service-status.ready svg{color:var(--rs-success)}.service-status.unavailable svg{color:var(--rs-warning)}
.collapsed{width:76px;flex-basis:76px;padding:24px 12px 16px}.collapsed .brand-copy,.collapsed .nav-label,.collapsed .nav-item span,.collapsed .workspace-id,.collapsed .sidebar-search span,.collapsed .sidebar-search kbd,.collapsed .user-copy,.collapsed .service-status span,.collapsed .active-pin{display:none}.collapsed .sidebar-topbar{flex-direction:column;margin:0 0 18px;gap:14px}.collapsed .sidebar-search,.collapsed .nav-item,.collapsed .sidebar-footer,.collapsed .service-status{justify-content:center}.collapsed .nav-item{padding:9px}.collapsed .nav-group{margin-bottom:12px}.collapsed .nav-scroll{margin-top:16px}.mobile-sidebar{position:relative;height:100dvh;width:264px;flex-basis:264px;border:0}.mobile-sidebar .sidebar-topbar{margin-right:25px}
@media(hover:hover) and (pointer:fine){.nav-item:hover{background:var(--rs-surface-soft);color:var(--rs-ink)}.nav-item.active:hover{background:var(--rs-primary-soft);color:var(--rs-primary)}}
</style>