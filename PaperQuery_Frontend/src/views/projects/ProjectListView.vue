<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { archiveProject, createProject, listProjects, restoreProject, type ResearchProject } from '@/api/project'

const router = useRouter()
const projects = ref<ResearchProject[]>([])
const showArchived = ref(false)
const name = ref('')
const description = ref('')
const goal = ref('')
const busy = ref(false)
async function load() { projects.value = await listProjects(showArchived.value) }
async function create() {
  if (!name.value.trim()) return ElMessage.warning('请输入项目名称')
  busy.value = true
  try {
    const project = await createProject(name.value.trim(), description.value, goal.value)
    await router.push(`/home/projects/${project.project_id}/overview`)
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '创建失败') }
  finally { busy.value = false }
}
async function changeStatus(project: ResearchProject) {
  try {
    if (project.status === 'archived') await restoreProject(project.project_id)
    else await archiveProject(project.project_id)
    await load()
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '操作失败') }
}
onMounted(load)
</script>

<template>
  <main class="project-page">
    <header><div><small>RESEARCHSPACE</small><h1>研究项目</h1><p>围绕研究问题组织论文、证据与成果。</p></div></header>
    <section class="create-card">
      <h2>新建研究项目</h2>
      <input v-model="name" maxlength="255" placeholder="项目名称" />
      <textarea v-model="description" placeholder="项目简介" rows="2" />
      <textarea v-model="goal" placeholder="研究目标" rows="2" />
      <button :disabled="busy" @click="create">创建项目</button>
    </section>
    <div class="list-heading"><h2>项目列表</h2><label><input v-model="showArchived" type="checkbox" @change="load" /> 显示归档</label></div>
    <div v-if="!projects.length" class="empty">暂无项目</div>
    <div class="project-grid">
      <article v-for="project in projects" :key="project.project_id" class="project-card">
        <small>{{ project.status === 'archived' ? '已归档' : '进行中' }}</small>
        <h3>{{ project.name }}</h3><p>{{ project.description || project.research_goal || '暂无简介' }}</p>
        <div><router-link v-if="project.status === 'active'" :to="`/home/projects/${project.project_id}/overview`">进入项目 →</router-link>
          <button @click="changeStatus(project)">{{ project.status === 'archived' ? '恢复' : '归档' }}</button></div>
      </article>
    </div>
  </main>
</template>

<style scoped>
.project-page{padding:40px;max-width:1160px;margin:auto;width:100%;color:#17233b}.project-page header small{color:#6b5bd0;font-weight:700;letter-spacing:.15em}.project-page h1{font-size:32px;margin:8px 0}.project-page p{color:#657086}.create-card,.project-card{background:white;border:1px solid #e4e8f1;border-radius:16px;padding:24px;box-shadow:0 8px 25px #192d5210}.create-card{display:grid;gap:12px;max-width:660px;margin:28px 0}.create-card h2{margin:0}.create-card input,.create-card textarea{border:1px solid #d9dfeb;border-radius:9px;padding:10px;font:inherit}.create-card button{justify-self:start;background:#5546b7;color:white;padding:10px 22px;border:0;border-radius:9px;cursor:pointer}.list-heading{display:flex;justify-content:space-between;align-items:center}.project-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}.project-card small{color:#6b5bd0}.project-card h3{font-size:19px;margin:12px 0}.project-card div{display:flex;justify-content:space-between;align-items:center}.project-card a{color:#5546b7;font-weight:600}.project-card button{border:0;background:none;color:#697388;cursor:pointer}.empty{padding:25px;color:#7c8798}
</style>
