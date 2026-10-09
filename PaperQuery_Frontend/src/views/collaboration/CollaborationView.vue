<script setup lang="ts">
import FeatureHeader from '@/components/research/FeatureHeader.vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  addComment,
  addMember,
  assignTask,
  listAssignments,
  listComments,
  listMembers,
  removeMember,
  type Assignment,
  type ProjectComment,
  type ProjectMember,
} from '@/api/collaboration'
import { listResearchTasks } from '@/api/research'
import { listClaims } from '@/api/evidence'
import { listComparisons } from '@/api/compare'
import { useResearchProjectStore } from '@/stores/researchProject'

const route = useRoute(),
  store = useResearchProjectStore(),
  id = String(route.params.projectId)
const members = ref<ProjectMember[]>([]),
  comments = ref<ProjectComment[]>([]),
  assignments = ref<Assignment[]>([])
const tasks = ref<any[]>([]),
  claims = ref<any[]>([]),
  comparisons = ref<any[]>([])
const pending = ref(''),
  loading = ref(true),
  error = ref('')
const roleLabel = (value: string) =>
  (
    ({ OWNER: '负责人', EDITOR: '编辑者', VIEWER: '观察者' }) as Record<
      string,
      string
    >
  )[value] || value
const username = ref(''),
  role = ref<ProjectMember['role']>('EDITOR')
const taskId = ref(''),
  assignee = ref('')
const targetType = ref('paper'),
  targetId = ref(''),
  comment = ref('')
const owner = computed(
  () =>
    members.value.some(
      (item) =>
        item.username === localStorage.getItem('username') &&
        item.role === 'OWNER',
    ) || store.currentProject?.created_by === localStorage.getItem('username'),
)
const targets = computed(() =>
  targetType.value === 'paper'
    ? store.projectDocuments.map((item) => ({
        id: item.document_id,
        name: item.document_name,
      }))
    : targetType.value === 'task'
      ? tasks.value.map((item) => ({ id: item.task_id, name: item.goal }))
      : targetType.value === 'claim'
        ? claims.value.map((item) => ({ id: item.claim_id, name: item.title }))
        : targetType.value === 'comparison'
          ? comparisons.value.map((item) => ({
              id: item.session_id,
              name: item.title,
            }))
          : [],
)
async function load() {
  loading.value = true
  error.value = ''
  try {
    const [
      memberRows,
      commentRows,
      assignmentRows,
      taskResult,
      claimRows,
      comparisonRows,
    ] = await Promise.all([
      listMembers(id),
      listComments(id),
      listAssignments(id),
      listResearchTasks(id),
      listClaims(id),
      listComparisons(id),
    ])
    members.value = memberRows
    comments.value = commentRows
    assignments.value = assignmentRows
    tasks.value = taskResult.data || []
    claims.value = claimRows
    comparisons.value = comparisonRows
  } catch {
    error.value = '协作信息暂时无法加载，请重试。'
  } finally {
    loading.value = false
  }
}
async function invite() {
  if (pending.value || !username.value.trim()) return
  pending.value = 'invite'
  try {
    await addMember(id, username.value.trim(), role.value)
    username.value = ''
    await load()
    ElMessage.success('项目成员已更新')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '添加失败')
  } finally {
    pending.value = ''
  }
}
async function remove(username: string) {
  try {
    await ElMessageBox.confirm(
      `将 ${username} 移出项目成员列表？`,
      '移除项目成员',
      {
        confirmButtonText: '移除成员',
        cancelButtonText: '取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }
  try {
    await removeMember(id, username)
    await load()
  } catch {
    ElMessage.error('成员移除失败，请重试')
  }
}
async function assign() {
  if (pending.value || !taskId.value || !assignee.value.trim()) return
  pending.value = 'assign'
  try {
    await assignTask(id, taskId.value, assignee.value.trim())
    assignee.value = ''
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '分配失败')
  } finally {
    pending.value = ''
  }
}
async function post() {
  if (pending.value) return
  if (!targetId.value || !comment.value.trim())
    return ElMessage.warning('请选择评论对象并填写内容')
  pending.value = 'post'
  try {
    await addComment(id, targetType.value, targetId.value, comment.value.trim())
    comment.value = ''
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '评论失败')
  } finally {
    pending.value = ''
  }
}
onMounted(load)
</script>

<template>
  <section class="rs-feature-page">
    <FeatureHeader
      eyebrow="PEOPLE / COLLABORATION"
      title="协作空间"
      description="让研究有共同的方向，也有清楚的责任与讨论。"
    />
    <p v-if="loading" class="rs-empty" aria-live="polite">正在连接协作空间…</p>
    <p v-else-if="error" class="rs-empty">
      {{ error }} <button @click="load">重新加载</button>
    </p>
    <div class="grid">
      <div class="panel">
        <h3>
          项目成员 <small>{{ members.length }}</small>
        </h3>
        <div v-for="member in members" :key="member.username" class="row">
          <span
            >{{ member.username }}
            <small>{{ roleLabel(member.role) }}</small></span
          ><button
            v-if="owner && member.username !== store.currentProject?.created_by"
            @click="remove(member.username)"
          >
            移除
          </button>
        </div>
        <div v-if="owner" class="form">
          <input
            aria-label="工作空间用户名"
            v-model="username"
            placeholder="工作空间用户名"
          /><select aria-label="项目角色" v-model="role">
            <option value="OWNER">负责人</option>
            <option value="EDITOR">编辑者</option>
            <option value="VIEWER">观察者</option></select
          ><button :disabled="!!pending || !username.trim()" @click="invite">
            {{ pending === 'invite' ? '添加中…' : '添加成员' }}
          </button>
        </div>
      </div>
      <div class="panel">
        <h3>
          任务分配 <small>{{ assignments.length }}</small>
        </h3>
        <div
          v-for="item in assignments"
          :key="item.task_id + item.username"
          class="row"
        >
          <span
            >{{ item.goal }} <small>→ {{ item.username }}</small></span
          >
        </div>
        <div class="form">
          <select aria-label="选择研究任务" v-model="taskId">
            <option value="">选择研究任务</option>
            <option
              v-for="task in tasks"
              :key="task.task_id"
              :value="task.task_id"
            >
              {{ task.goal }}
            </option></select
          ><input
            aria-label="负责人用户名"
            v-model="assignee"
            placeholder="负责人用户名"
          /><button
            :disabled="!!pending || !taskId || !assignee.trim()"
            @click="assign"
          >
            {{ pending === 'assign' ? '分配中…' : '分配任务' }}
          </button>
        </div>
      </div>
    </div>
    <div class="panel comments">
      <h3>
        研究评论 <small>{{ comments.length }}</small>
      </h3>
      <div class="form">
        <select
          aria-label="评论对象类型"
          v-model="targetType"
          @change="targetId = ''"
        >
          <option value="paper">论文</option>
          <option value="claim">观点</option>
          <option value="comparison">比较</option>
          <option value="task">任务</option>
          <option value="artifact">成果</option></select
        ><select
          aria-label="评论对象"
          v-if="targetType !== 'artifact'"
          v-model="targetId"
        >
          <option value="">选择对象</option>
          <option v-for="target in targets" :key="target.id" :value="target.id">
            {{ target.name }}
          </option></select
        ><input
          aria-label="评论对象"
          v-else
          v-model="targetId"
          placeholder="成果 ID"
        /><textarea
          aria-label="讨论内容"
          v-model="comment"
          rows="2"
          placeholder="写下讨论内容"
        /><button
          :disabled="!!pending || !targetId || !comment.trim()"
          @click="post"
        >
          {{ pending === 'post' ? '发布中…' : '发表评论' }}
        </button>
      </div>
      <div v-for="item in comments" :key="item.comment_id" class="comment">
        <strong>{{ item.username }}</strong
        ><small
          >{{ item.target_type }} · {{ item.target_id }} ·
          {{
            item.created_at ? new Date(item.created_at).toLocaleString() : ''
          }}</small
        >
        <p>{{ item.content }}</p>
      </div>
      <p v-if="!comments.length">暂无评论。</p>
    </div>
  </section>
</template>

<style scoped>
.rs-feature-page {
  min-width: 0;
  overflow-wrap: anywhere;
}
.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
.panel {
  background: white;
  border: 1px solid #e0e6f0;
  border-radius: 13px;
  padding: 20px;
  margin: 14px 0;
}
.panel h3 {
  margin-top: 0;
}
.row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #edf0f5;
}
.row small {
  color: #6d5ec2;
}
.row button {
  border: 0;
  background: none;
  color: #a25f69;
  cursor: pointer;
}
.form {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 15px;
}
.form input,
.form select,
.form textarea {
  min-width: 160px;
  flex: 1;
  border: 1px solid #d8dfeb;
  border-radius: 8px;
  padding: 9px;
}
.form textarea {
  flex-basis: 100%;
}
.form button {
  border: 0;
  border-radius: 8px;
  background: #5546b7;
  color: white;
  padding: 9px 16px;
  cursor: pointer;
}
.comment {
  border-top: 1px solid #e8edf4;
  padding: 13px 0;
}
.comment small {
  display: block;
  color: #8390a0;
}
.comment p {
  margin: 5px 0;
}
@media (max-width: 850px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
.rs-feature-page
  :is(.create, .setup, .result, .claim, .panel, .workspace aside) {
  border-color: var(--rs-line);
  border-radius: 14px;
  box-shadow: none;
}
.rs-feature-page :is(.create, .setup, .form, .bar, .citation-form) > button,
.rs-feature-page .picker > button {
  background: var(--rs-primary);
}
</style>
