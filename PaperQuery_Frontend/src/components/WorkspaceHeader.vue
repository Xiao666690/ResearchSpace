<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useStore } from 'vuex'
import { Menu, Search, ChevronRight, LogOut, UserRound, ArrowUpRight, X } from 'lucide-vue-next'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '@/components/ui/dialog'
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuSeparator } from '@/components/ui/dropdown-menu'
import { getSidebarGroups } from './utils/sidebar'
const emit=defineEmits<{(e:'openNavigation'):void}>()
const route=useRoute(), router=useRouter(), store=useStore()
const username=localStorage.getItem('username') || '研究者'
const searchOpen=ref(false), query=ref('')
const searchInput=ref<HTMLInputElement|null>(null)
const titles:Record<string,string>={dashboard:'今日概览',projects:'研究项目',library:'论文资料',knowledge:'知识库',pdfinfo:'论文阅读',notes:'科研笔记',chat:'智能问答',research:'研究任务',timeline:'研究时间线',compare:'方法比较',evidence:'证据看板',studio:'成果工作室',map:'研究图谱',collaboration:'协作空间',team:'团队管理',note:'科研笔记',overview:'项目概览'}
const title=computed(()=> { const segments=route.path.toLowerCase().split('/'); for(let i=segments.length-1;i>=0;i--) if(titles[segments[i]]) return titles[segments[i]]; return '研究工作台' })
const projectId=computed(()=> typeof route.params.projectId==='string'?route.params.projectId:null)
const destinations=computed(()=> getSidebarGroups(localStorage.getItem('role'),projectId.value).flatMap(group=>group.items.map(item=>({...item,group:group.title}))).filter(item=>!query.value || item.title.toLowerCase().includes(query.value.toLowerCase()) || item.group.includes(query.value)))
function openSearch(){query.value='';searchOpen.value=true}
function navigate(link:string){searchOpen.value=false;router.push(link)}
async function logout(){ await store.dispatch('logout'); await router.push('/login') }
function onSearchKey(event:KeyboardEvent){
 if(!['ArrowDown','ArrowUp'].includes(event.key)) return
 const buttons=Array.from(document.querySelectorAll<HTMLButtonElement>('.command-result'))
 if(!buttons.length) return
 event.preventDefault()
 const current=buttons.indexOf(document.activeElement as HTMLButtonElement)
 const next=event.key==='ArrowDown'?(current+1)%buttons.length:(current<=0?buttons.length-1:current-1)
 buttons[next].focus()
}
function onShortcut(event:KeyboardEvent){if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k'){event.preventDefault();openSearch()}}
onMounted(()=>window.addEventListener('keydown',onShortcut))
onBeforeUnmount(()=>window.removeEventListener('keydown',onShortcut))
watch(searchOpen,async value=>{if(value){await new Promise(resolve=>setTimeout(resolve,0));searchInput.value?.focus()}})
defineExpose({openSearch})
</script>
<template>
  <header class="workspace-header">
    <div class="header-location"><button type="button" class="mobile-menu rs-button" aria-label="打开导航" @click="emit('openNavigation')"><Menu :size="19"/></button><router-link class="header-home" to="/home/dashboard">研究空间</router-link><ChevronRight :size="13" class="crumb-separator"/><span class="current-location">{{ title }}</span><span v-if="projectId" class="project-context">项目内</span></div>
    <div class="header-actions"><button type="button" class="header-search rs-button" aria-label="搜索功能（Control 或 Command K）" @click="openSearch"><Search :size="15"/><span>查找功能</span><kbd>⌘ K</kbd></button><span class="header-divider"/>
      <DropdownMenu><DropdownMenuTrigger as-child><button type="button" class="account-button rs-button" aria-label="账户菜单"><span class="account-avatar">{{ username.slice(0,1).toUpperCase() }}</span><span class="account-name">{{ username }}</span></button></DropdownMenuTrigger><DropdownMenuContent align="end" class="w-48"><div class="account-caption"><UserRound :size="14"/><span>{{ username }}</span></div><DropdownMenuSeparator/><DropdownMenuItem @select="navigate('/home/projects')">我的研究项目</DropdownMenuItem><DropdownMenuItem @select="logout"><LogOut class="mr-2 h-4 w-4"/>退出登录</DropdownMenuItem></DropdownMenuContent></DropdownMenu>
    </div>
  </header>
  <Dialog v-model:open="searchOpen"><DialogContent class="search-dialog" ><DialogHeader><DialogTitle>前往研究空间</DialogTitle><DialogDescription>查找项目、资料和研究工具。使用方向键与 Tab 浏览，Enter 打开。</DialogDescription></DialogHeader><label for="workspace-search" class="sr-only">搜索功能名称</label><div class="command-input"><Search :size="18"/><input id="workspace-search" @keydown="onSearchKey" ref="searchInput" v-model="query" placeholder="输入功能名称…" autocomplete="off"/><button v-if="query" type="button" aria-label="清空搜索" @click="query='' "><X :size="16"/></button></div><div class="command-results" @keydown="onSearchKey"><button v-for="item in destinations" :key="item.link" type="button" class="command-result" @click="navigate(item.link)"><span class="command-icon"><component :is="item.icon" :size="18"/></span><span><strong>{{ item.title }}</strong><small>{{ item.group }}</small></span><ArrowUpRight :size="14"/></button><div v-if="!destinations.length" class="command-empty">没有匹配的功能，试试“论文”或“研究”。</div></div></DialogContent></Dialog>
</template>
<style scoped>
.workspace-header{position:sticky;top:0;z-index:15;display:flex;justify-content:space-between;align-items:center;gap:16px;min-height:64px;padding:12px clamp(18px,2.5vw,36px);border-bottom:1px solid var(--rs-line);background:var(--rs-canvas)}.header-location,.header-actions{display:flex;align-items:center;gap:12px;min-width:0}.header-home{font-size:12px;color:var(--rs-muted);text-decoration:none;white-space:nowrap}.crumb-separator{color:#a0a3a8;flex:none}.current-location{font-size:12px;font-weight:550;white-space:nowrap}.project-context{font-size:10px;padding:2px 6px;border:1px solid var(--rs-line);border-radius:5px;color:var(--rs-muted);white-space:nowrap}.header-search{display:flex;align-items:center;gap:8px;font-size:11px;color:var(--rs-muted);padding:7px 9px;border-radius:7px}.header-search kbd{font-size:9px;margin-left:8px;color:#8b9097}.header-divider{height:18px;width:1px;background:var(--rs-line)}.account-button{display:flex;align-items:center;gap:8px;font-size:11px;max-width:150px;border-radius:8px}.account-avatar{width:28px;height:28px;border-radius:50%;background:var(--rs-primary-soft);color:var(--rs-primary);display:grid;place-items:center;border:1px solid rgb(104 88 214 / .12);flex:none}.account-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.account-caption{display:flex;gap:8px;padding:9px;font-size:12px;color:var(--rs-muted);overflow-wrap:anywhere}.mobile-menu{display:none;width:32px;height:32px;border-radius:8px;color:var(--rs-ink)}.command-input{display:flex;align-items:center;gap:12px;padding:12px 14px;border:1px solid var(--rs-line);border-radius:10px;color:var(--rs-muted)}.command-input input{width:100%;min-width:0;background:transparent;border:0;font-size:15px;outline:none}.command-input input:focus-visible{outline:none}.command-input:focus-within{border-color:var(--rs-primary);box-shadow:0 0 0 3px var(--rs-primary-soft)}.command-results{max-height:380px;overflow:auto}.command-result{display:flex;align-items:center;gap:12px;width:100%;padding:10px 8px;text-align:left;border-radius:8px}.command-icon{display:grid;place-items:center;width:34px;height:34px;background:var(--rs-canvas);border:1px solid var(--rs-line);border-radius:8px;color:var(--rs-primary)}.command-result strong{display:block;font-size:13px;font-weight:550}.command-result small{font-size:10px;color:var(--rs-muted)}.command-result>svg{margin-left:auto;color:var(--rs-muted)}.command-result:hover{background:var(--rs-primary-soft)}.command-empty{font-size:13px;text-align:center;color:var(--rs-muted);padding:32px 10px}
@media(max-width:767px){.mobile-menu{display:grid;place-items:center}.header-home,.crumb-separator,.project-context,.header-search span,.header-search kbd,.account-name{display:none}.workspace-header{padding:10px 16px;min-height:58px}.header-location,.header-actions{gap:8px}.header-search{width:32px;height:32px;justify-content:center}}
</style>