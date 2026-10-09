<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { projectOverview, updateProject } from '@/api/project'
import { useResearchProjectStore } from '@/stores/researchProject'
const route = useRoute()
const overview = ref<any>(null)
const store = useResearchProjectStore()
const editing = ref(false),
  saving = ref(false),
  loading = ref(true),
  error = ref('')
const name = ref(''),
  description = ref(''),
  goal = ref('')
function beginEdit() {
  name.value = store.currentProject?.name || ''
  description.value = store.currentProject?.description || ''
  goal.value = store.currentProject?.research_goal || ''
  editing.value = true
}
async function save() {
  if (!name.value.trim() || saving.value) return
  saving.value = true
  try {
    await updateProject(String(route.params.projectId), {
      name: name.value,
      description: description.value,
      research_goal: goal.value,
    })
    await store.loadCurrentProject(String(route.params.projectId))
    overview.value = await projectOverview(String(route.params.projectId))
    editing.value = false
    ElMessage.success('项目已更新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
async function load() {
  loading.value = true
  error.value = ''
  try {
    overview.value = await projectOverview(String(route.params.projectId))
  } catch {
    error.value = '项目概览加载失败'
  } finally {
    loading.value = false
  }
}
onMounted(load)
</script>

<template>
  <section class="rs-feature-page">
    <div class="heading">
      <div>
        <p class="rs-kicker">MISSION / OVERVIEW</p>
        <h2>研究全景</h2>
      </div>
      <button @click="beginEdit">编辑项目</button>
    </div>
    <p>
      {{
        overview?.project?.description || '为项目添加论文，开始构建研究脉络。'
      }}
    </p>
    <div v-if="editing" class="edit">
      <input
        aria-label="项目名称"
        v-model="name"
        maxlength="255"
        placeholder="项目名称"
      /><textarea
        aria-label="项目简介"
        v-model="description"
        rows="2"
        placeholder="项目简介"
      /><textarea
        aria-label="研究目标"
        v-model="goal"
        rows="2"
        placeholder="研究目标"
      />
      <div>
        <button :disabled="saving || !name.trim()" @click="save">
          {{ saving ? '保存中…' : '保存项目' }}</button
        ><button @click="editing = false">取消</button>
      </div>
    </div>
    <p v-if="loading" aria-live="polite">正在整理项目全景…</p>
    <p v-if="error" class="rs-empty">
      {{ error }} <button @click="load">重试</button>
    </p>
    <div class="mission-goal">
      <small>RESEARCH QUESTION</small>
      <h3>
        {{ store.currentProject?.research_goal || '为研究设定一个清晰的目标' }}
      </h3>
      <router-link :to="`/home/projects/${route.params.projectId}/research`"
        >从这里开始研究 ↗</router-link
      >
    </div>
    <div class="stats">
      <router-link :to="`/home/projects/${route.params.projectId}/library`"
        ><b>{{ overview?.document_count ?? '—' }}</b
        ><span>项目论文 ↗</span></router-link
      ><router-link :to="`/home/projects/${route.params.projectId}/research`"
        ><b>{{ overview?.task_count ?? '—' }}</b
        ><span>研究任务 ↗</span></router-link
      ><router-link :to="`/home/projects/${route.params.projectId}/studio`"
        ><b>{{ overview?.artifact_count ?? '—' }}</b
        ><span>研究成果 ↗</span></router-link
      ><router-link :to="`/home/projects/${route.params.projectId}/timeline`"
        ><b>{{ overview?.event_count ?? '—' }}</b
        ><span>项目动态 ↗</span></router-link
      >
    </div>
  </section>
</template>

<style scoped>
.heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.heading button,
.edit button {
  background: #5546b7;
  color: white;
  border: 0;
  border-radius: 8px;
  padding: 8px 15px;
  cursor: pointer;
}
.edit {
  display: grid;
  gap: 10px;
  max-width: 660px;
  padding: 20px;
  background: white;
  border: 1px solid #e2e7f1;
  border-radius: 12px;
}
.edit input,
.edit textarea {
  border: 1px solid #d8e0eb;
  border-radius: 8px;
  padding: 9px;
}
.edit > div {
  display: flex;
  gap: 8px;
}
.edit > div button:last-child {
  background: #e9ecf4;
  color: #59667a;
}
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 14px;
  margin-top: 22px;
}
.stats div {
  display: flex;
  flex-direction: column;
  padding: 22px;
  background: white;
  border: 1px solid #e2e7f1;
  border-radius: 13px;
}
.stats b {
  font-size: 28px;
  color: #5546b7;
}
.stats span {
  color: #677489;
}
.stats > a {
  display: flex;
  flex-direction: column;
  padding: 24px;
  border: 1px solid var(--rs-line);
  border-radius: 12px;
  background: white;
  text-decoration: none;
  gap: 8px;
}
.stats b {
  font-variant-numeric: tabular-nums;
  font-weight: 500;
  font-size: 36px;
  color: var(--rs-ink);
}
.stats span {
  font-size: 12px;
  color: var(--rs-muted);
}
.mission-goal {
  margin: 26px 0;
  padding: 28px 30px;
  background: #f0eef8;
  border: 1px solid #e4e0f1;
  border-radius: 14px;
}
.mission-goal small {
  font-size: 10px;
  letter-spacing: 0.15em;
  color: var(--rs-primary);
}
.mission-goal h3 {
  font-size: 22px;
  font-weight: 500;
  line-height: 1.6;
  margin: 12px 0 20px;
  overflow-wrap: anywhere;
}
.mission-goal a {
  font-size: 13px;
  color: var(--rs-primary);
}
.rs-kicker {
  font-size: 10px;
  letter-spacing: 0.16em;
  color: var(--rs-primary);
  margin: 0 0 8px;
}
.heading h2 {
  font-size: 28px;
  font-weight: 600;
  margin: 0;
}
.edit {
  margin-top: 20px;
}
.stats {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}
@media (max-width: 800px) {
  .stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .mission-goal {
    padding: 22px;
  }
}
</style>
