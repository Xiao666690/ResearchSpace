<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useResearchProjectStore } from '@/stores/researchProject'

const route = useRoute()
const router = useRouter()
const store = useResearchProjectStore()
async function load(id: string) {
  try { await store.loadCurrentProject(id) }
  catch { ElMessage.error('项目不存在或无权访问'); await router.replace('/home/projects') }
}
onMounted(() => load(String(route.params.projectId)))
watch(() => route.params.projectId, id => { if (id) load(String(id)) })
const tabs = [
  ['overview', '概览'], ['library', '论文'], ['map', '研究图谱'], ['evidence', '证据看板'],
  ['compare', '比较实验室'], ['research', '研究任务'], ['timeline', '时间线'],
  ['studio', '成果工作室'], ['collaboration', '协作'],
]
</script>

<template>
  <div class="project-layout">
    <header><router-link to="/home/projects">← 全部项目</router-link><h1>{{ store.currentProject?.name || '研究项目' }}</h1><p>{{ store.currentProject?.research_goal }}</p></header>
    <nav><router-link v-for="[path,label] in tabs" :key="path" :to="`/home/projects/${route.params.projectId}/${path}`">{{ label }}</router-link></nav>
    <router-view v-if="store.currentProjectId === route.params.projectId" />
  </div>
</template>

<style scoped>
.project-layout{width:100%;min-width:0;padding:28px 32px;color:#18253c}.project-layout header a{color:#6659bc}.project-layout h1{font-size:26px;margin:10px 0 3px}.project-layout header p{color:#66748a}.project-layout nav{display:flex;gap:6px;overflow-x:auto;border-bottom:1px solid #dfe5ef;margin:20px 0;white-space:nowrap}.project-layout nav a{padding:11px 13px;text-decoration:none;color:#66748a;border-bottom:2px solid transparent}.project-layout nav a.router-link-active{color:#5546b7;border-color:#5546b7;font-weight:650}
</style>
