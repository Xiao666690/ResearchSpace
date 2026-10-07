<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectOverview, updateProject } from '@/api/project'
import { useResearchProjectStore } from '@/stores/researchProject'
const route = useRoute()
const overview = ref<any>(null)
const store = useResearchProjectStore()
const editing = ref(false)
const name = ref(''), description = ref(''), goal = ref('')
function beginEdit() { name.value = store.currentProject?.name || ''; description.value = store.currentProject?.description || ''; goal.value = store.currentProject?.research_goal || ''; editing.value = true }
async function save() {
  try { await updateProject(String(route.params.projectId), { name: name.value, description: description.value, research_goal: goal.value }); await store.loadCurrentProject(String(route.params.projectId)); overview.value = await projectOverview(String(route.params.projectId)); editing.value = false; ElMessage.success('项目已更新') }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '保存失败') }
}
onMounted(async () => { overview.value = await projectOverview(String(route.params.projectId)) })
</script>

<template>
  <section><div class="heading"><h2>项目概览</h2><button @click="beginEdit">编辑项目</button></div><p>{{ overview?.project?.description || '为项目添加论文，开始构建研究脉络。' }}</p>
    <div v-if="editing" class="edit"><input v-model="name" maxlength="255" placeholder="项目名称" /><textarea v-model="description" rows="2" placeholder="项目简介" /><textarea v-model="goal" rows="2" placeholder="研究目标" /><div><button @click="save">保存</button><button @click="editing=false">取消</button></div></div>
    <div class="stats"><div><b>{{ overview?.document_count ?? '—' }}</b><span>项目论文</span></div><div><b>{{ overview?.task_count ?? '—' }}</b><span>研究任务</span></div><div><b>{{ overview?.artifact_count ?? '—' }}</b><span>研究成果</span></div><div><b>{{ overview?.event_count ?? '—' }}</b><span>项目动态</span></div></div>
  </section>
</template>

<style scoped>.heading{display:flex;justify-content:space-between;align-items:center}.heading button,.edit button{background:#5546b7;color:white;border:0;border-radius:8px;padding:8px 15px;cursor:pointer}.edit{display:grid;gap:10px;max-width:660px;padding:20px;background:white;border:1px solid #e2e7f1;border-radius:12px}.edit input,.edit textarea{border:1px solid #d8e0eb;border-radius:8px;padding:9px}.edit>div{display:flex;gap:8px}.edit>div button:last-child{background:#e9ecf4;color:#59667a}.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-top:22px}.stats div{display:flex;flex-direction:column;padding:22px;background:white;border:1px solid #e2e7f1;border-radius:13px}.stats b{font-size:28px;color:#5546b7}.stats span{color:#677489}</style>
