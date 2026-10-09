<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  archiveProject,
  createProject,
  listProjects,
  restoreProject,
  type ResearchProject,
} from '@/api/project'

const router = useRouter()
const projects = ref<ResearchProject[]>([])
const showArchived = ref(false)
const name = ref('')
const description = ref('')
const goal = ref('')
const busy = ref(false),
  changingStatus = ref('')
const creating = ref(false),
  search = ref(''),
  loading = ref(true),
  error = ref('')
const filtered = computed(() =>
  projects.value.filter((item) =>
    `${item.name} ${item.description} ${item.research_goal}`
      .toLowerCase()
      .includes(search.value.toLowerCase()),
  ),
)
async function load() {
  loading.value = true
  error.value = ''
  try {
    projects.value = await listProjects(showArchived.value)
  } catch {
    error.value = '项目暂时无法加载，请重试。'
  } finally {
    loading.value = false
  }
}
async function create() {
  if (busy.value) return
  if (!name.value.trim()) return ElMessage.warning('请输入项目名称')
  busy.value = true
  try {
    const project = await createProject(
      name.value.trim(),
      description.value,
      goal.value,
    )
    await router.push(`/home/projects/${project.project_id}/overview`)
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '创建失败')
  } finally {
    busy.value = false
  }
}
async function changeStatus(project: ResearchProject) {
  if (changingStatus.value) return
  changingStatus.value = project.project_id
  try {
    if (project.status === 'archived') await restoreProject(project.project_id)
    else await archiveProject(project.project_id)
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '操作失败')
  } finally {
    changingStatus.value = ''
  }
}
onMounted(load)
</script>

<template>
  <main class="project-page">
    <header>
      <div>
        <small>MISSIONS / RESEARCHSPACE</small>
        <h1>每一个问题，都是新的起点。</h1>
        <p>在这里连接论文、证据与成果，建立自己的研究方向。</p>
      </div>
      <button
        class="new-project"
        :aria-expanded="creating"
        @click="creating = !creating"
      >
        {{ creating ? '收起表单' : '＋ 新建项目' }}
      </button>
    </header>
    <section v-if="creating" class="create-card">
      <h2>新建研究项目</h2>
      <label
        >项目名称<input
          aria-label="项目名称"
          v-model="name"
          maxlength="255"
          placeholder="为这次探索命名"
      /></label>
      <label
        >项目简介<textarea
          aria-label="项目简介"
          v-model="description"
          placeholder="这个项目关注什么？"
          rows="2"
        />
      </label>
      <label
        >研究目标<textarea
          aria-label="研究目标"
          v-model="goal"
          placeholder="希望找到怎样的答案？"
          rows="2"
        />
      </label>
      <button :disabled="busy || !name.trim()" @click="create">
        {{ busy ? '正在创建…' : '创建研究项目 →' }}
      </button>
    </section>
    <div class="list-heading">
      <h2>
        研究档案 <small>{{ filtered.length }}</small>
      </h2>
      <input
        v-model="search"
        class="project-search"
        aria-label="搜索研究项目"
        placeholder="搜索项目或研究目标"
      /><label
        ><input v-model="showArchived" type="checkbox" @change="load" />
        显示归档</label
      >
    </div>
    <div v-if="loading" class="empty" aria-live="polite">正在打开研究档案…</div>
    <div v-else-if="error" class="empty">
      {{ error }} <button @click="load">重新加载</button>
    </div>
    <div v-else-if="!filtered.length" class="empty">
      <strong>{{
        search ? '没有匹配的项目' : '研究旅程，从一个问题开始'
      }}</strong>
      <p>
        {{
          search
            ? '尝试其他关键词。'
            : '创建项目，将论文、观点与成果组织在一起。'
        }}
      </p>
      <button v-if="!search" @click="creating = true">创建第一个项目</button>
    </div>
    <div class="project-grid">
      <article
        v-for="(project, index) in filtered"
        :key="project.project_id"
        class="project-card"
      >
        <div class="project-card-top">
          <span class="mission-number">{{
            String(index + 1).padStart(2, '0')
          }}</span
          ><small>{{
            project.status === 'archived' ? '已归档' : '进行中'
          }}</small>
        </div>
        <h3>{{ project.name }}</h3>
        <p>{{ project.description || project.research_goal || '暂无简介' }}</p>
        <div class="project-card-actions">
          <router-link
            v-if="project.status === 'active'"
            :to="`/home/projects/${project.project_id}/overview`"
            >进入项目 →</router-link
          >
          <button :disabled="!!changingStatus" @click="changeStatus(project)">
            {{
              changingStatus === project.project_id
                ? '处理中…'
                : project.status === 'archived'
                  ? '恢复'
                  : '归档'
            }}
          </button>
        </div>
      </article>
    </div>
  </main>
</template>

<style scoped>
.project-page {
  padding: 40px;
  max-width: 1160px;
  margin: auto;
  width: 100%;
  color: #17233b;
}
.project-page header small {
  color: #6b5bd0;
  font-weight: 700;
  letter-spacing: 0.15em;
}
.project-page h1 {
  font-size: 32px;
  margin: 8px 0;
}
.project-page p {
  color: #657086;
}
.create-card,
.project-card {
  background: white;
  border: 1px solid #e4e8f1;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 25px #192d5210;
}
.create-card {
  display: grid;
  gap: 12px;
  max-width: 660px;
  margin: 28px 0;
}
.create-card h2 {
  margin: 0;
}
.create-card input,
.create-card textarea {
  border: 1px solid #d9dfeb;
  border-radius: 9px;
  padding: 10px;
  font: inherit;
}
.create-card button {
  justify-self: start;
  background: #5546b7;
  color: white;
  padding: 10px 22px;
  border: 0;
  border-radius: 9px;
  cursor: pointer;
}
.list-heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.project-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.project-card small {
  color: #6b5bd0;
}
.project-card h3 {
  font-size: 19px;
  margin: 12px 0;
}
.project-card div {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.project-card a {
  color: #5546b7;
  font-weight: 600;
}
.project-card button {
  border: 0;
  background: none;
  color: #697388;
  cursor: pointer;
}
.empty {
  padding: 25px;
  color: #7c8798;
}
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}
.project-page {
  max-width: 1240px;
  padding: 40px clamp(16px, 4vw, 48px);
}
.project-page h1 {
  font-size: clamp(25px, 3vw, 36px);
  font-weight: 600;
  letter-spacing: -0.04em;
}
.new-project,
.empty button {
  background: var(--rs-primary);
  color: white;
  padding: 11px 18px;
  border: 0;
  border-radius: 8px;
  white-space: nowrap;
}
.create-card {
  max-width: none;
  grid-template-columns: 1fr 1fr;
  background: #fff;
  box-shadow: none;
  border-radius: 14px;
}
.create-card h2,
.create-card label:first-of-type {
  grid-column: 1/-1;
}
.create-card label {
  display: grid;
  gap: 8px;
  font-size: 12px;
  color: var(--rs-muted);
}
.project-search {
  padding: 10px 12px;
  background: white;
  border: 1px solid var(--rs-line);
  border-radius: 8px;
  min-width: 230px;
}
.list-heading {
  gap: 16px;
  flex-wrap: wrap;
  margin: 30px 0 20px;
}
.list-heading h2 {
  font-size: 18px;
}
.list-heading small {
  font-size: 12px;
  color: var(--rs-muted);
  margin-left: 10px;
}
.project-grid {
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}
.project-card {
  padding: 24px;
  border: 1px solid var(--rs-line);
  border-radius: 14px;
  box-shadow: none;
  display: flex;
  flex-direction: column;
  min-height: 224px;
}
.project-card-top {
  display: flex;
  justify-content: space-between !important;
}
.mission-number {
  font-family: monospace;
  color: #aaa4bb;
  font-size: 12px;
}
.project-card small {
  padding: 4px 8px;
  background: #f0eef9;
  border-radius: 5px;
  font-size: 11px;
}
.project-card h3 {
  line-height: 1.5;
  overflow-wrap: anywhere;
}
.project-card p {
  font-size: 13px;
  line-height: 1.7;
  flex: 1;
}
.project-card-actions {
  padding-top: 18px;
  border-top: 1px solid var(--rs-line);
  font-size: 12px;
}
.empty {
  padding: 48px;
  text-align: center;
  border: 1px dashed var(--rs-line);
  border-radius: 14px;
  line-height: 1.8;
}
@media (max-width: 650px) {
  header {
    align-items: flex-start;
    flex-direction: column;
  }
  .create-card {
    grid-template-columns: 1fr;
  }
  .list-heading {
    align-items: flex-start;
  }
  .project-search {
    width: 100%;
    order: 3;
  }
  .empty {
    padding: 28px;
  }
}
</style>
