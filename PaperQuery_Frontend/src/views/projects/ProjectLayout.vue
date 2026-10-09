<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useResearchProjectStore } from '@/stores/researchProject'

const route = useRoute()
const router = useRouter()
const store = useResearchProjectStore()
async function load(id: string) {
  try {
    await store.loadCurrentProject(id)
  } catch {
    ElMessage.error('项目不存在或无权访问')
    await router.replace('/home/projects')
  }
}
onMounted(() => load(String(route.params.projectId)))
watch(
  () => route.params.projectId,
  (id) => {
    if (id) load(String(id))
  },
)
const tabs = [
  ['overview', '概览'],
  ['library', '论文'],
  ['map', '研究图谱'],
  ['evidence', '证据看板'],
  ['compare', '比较实验室'],
  ['chat', '智能问答'],
  ['research', '研究任务'],
  ['timeline', '时间线'],
  ['studio', '成果工作室'],
  ['collaboration', '协作'],
]
</script>

<template>
  <div class="project-layout">
    <header class="project-context">
      <router-link to="/home/projects">← 全部项目</router-link>
      <p class="rs-kicker">RESEARCH MISSION</p>
      <h1>{{ store.currentProject?.name || '研究项目' }}</h1>
      <p>{{ store.currentProject?.research_goal }}</p>
    </header>
    <nav aria-label="项目功能导航">
      <router-link
        v-for="[path, label] in tabs"
        :key="path"
        :to="`/home/projects/${route.params.projectId}/${path}`"
        >{{ label }}</router-link
      >
    </nav>
    <router-view
      :key="String(route.params.projectId)"
      v-if="store.currentProjectId === route.params.projectId"
    />
  </div>
</template>

<style scoped>
.project-layout {
  width: 100%;
  min-width: 0;
  padding: 28px 32px;
  color: #18253c;
}
.project-layout header a {
  color: #6659bc;
}
.project-layout h1 {
  font-size: 26px;
  margin: 10px 0 3px;
}
.project-layout header p {
  color: #66748a;
}
.project-layout nav {
  display: flex;
  gap: 6px;
  overflow-x: auto;
  border-bottom: 1px solid #dfe5ef;
  margin: 20px 0;
  white-space: nowrap;
}
.project-layout nav a {
  padding: 11px 13px;
  text-decoration: none;
  color: #66748a;
  border-bottom: 2px solid transparent;
}
.project-layout nav a.router-link-active {
  color: #5546b7;
  border-color: #5546b7;
  font-weight: 650;
}
.project-layout {
  color: var(--rs-ink);
  padding: 30px clamp(16px, 3vw, 40px);
  max-width: 1500px;
  margin: 0 auto;
}
.project-context {
  border-bottom: 1px solid var(--rs-line);
  padding-bottom: 22px;
}
.project-context > a {
  font-size: 12px;
}
.project-context .rs-kicker {
  font-size: 10px;
  letter-spacing: 0.18em;
  margin: 22px 0 8px;
  color: var(--rs-primary);
}
.project-layout h1 {
  font-size: 32px;
  letter-spacing: -0.035em;
  font-weight: 600;
  overflow-wrap: anywhere;
}
.project-layout nav {
  gap: 2px;
  margin: 20px 0 30px;
  scrollbar-width: thin;
}
.project-layout nav a {
  border-radius: 8px 8px 0 0;
  padding: 12px 14px;
  font-size: 13px;
}
.project-layout nav a.router-link-active {
  background: #efedf9;
  color: var(--rs-primary);
  border-color: var(--rs-primary);
}
.project-layout :deep(.chat-workspace) {
  height: min(720px, calc(100dvh - 280px));
  min-height: 440px;
  border: 1px solid var(--rs-line);
  border-radius: 14px;
}
.project-layout :deep(.research-page) {
  padding: 0 0 30px;
}
@media (max-width: 600px) {
  .project-layout h1 {
    font-size: 26px;
  }
  .project-layout nav {
    margin-bottom: 24px;
  }
  .project-layout :deep(.chat-workspace) {
    height: 680px;
  }
}
</style>
