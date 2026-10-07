<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { addComment, addMember, assignTask, listAssignments, listComments, listMembers,
  removeMember, type Assignment, type ProjectComment, type ProjectMember } from '@/api/collaboration'
import { listResearchTasks } from '@/api/research'
import { listClaims } from '@/api/evidence'
import { listComparisons } from '@/api/compare'
import { useResearchProjectStore } from '@/stores/researchProject'

const route = useRoute(), store = useResearchProjectStore(), id = String(route.params.projectId)
const members = ref<ProjectMember[]>([]), comments = ref<ProjectComment[]>([]), assignments = ref<Assignment[]>([])
const tasks = ref<any[]>([]), claims = ref<any[]>([]), comparisons = ref<any[]>([])
const username = ref(''), role = ref<ProjectMember['role']>('EDITOR')
const taskId = ref(''), assignee = ref('')
const targetType = ref('paper'), targetId = ref(''), comment = ref('')
const owner = computed(() => members.value.some(item => item.username === localStorage.getItem('username') && item.role === 'OWNER') || store.currentProject?.created_by === localStorage.getItem('username'))
const targets = computed(() => targetType.value === 'paper'
  ? store.projectDocuments.map(item => ({id:item.document_id, name:item.document_name}))
  : targetType.value === 'task' ? tasks.value.map(item => ({id:item.task_id,name:item.goal}))
  : targetType.value === 'claim' ? claims.value.map(item => ({id:item.claim_id,name:item.title}))
  : targetType.value === 'comparison' ? comparisons.value.map(item => ({id:item.session_id,name:item.title})) : [])
async function load() {
  const [memberRows, commentRows, assignmentRows, taskResult, claimRows, comparisonRows] = await Promise.all([
    listMembers(id), listComments(id), listAssignments(id), listResearchTasks(id), listClaims(id), listComparisons(id)])
  members.value = memberRows; comments.value = commentRows; assignments.value = assignmentRows
  tasks.value = taskResult.data || []; claims.value = claimRows; comparisons.value = comparisonRows
}
async function invite() {
  try { await addMember(id, username.value.trim(), role.value); username.value=''; await load(); ElMessage.success('项目成员已更新') }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '添加失败') }
}
async function remove(username: string) { await removeMember(id, username); await load() }
async function assign() {
  if (!taskId.value || !assignee.value.trim()) return
  try { await assignTask(id, taskId.value, assignee.value.trim()); assignee.value=''; await load() }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '分配失败') }
}
async function post() {
  if (!targetId.value || !comment.value.trim()) return ElMessage.warning('请选择评论对象并填写内容')
  try { await addComment(id, targetType.value, targetId.value, comment.value.trim()); comment.value=''; await load() }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '评论失败') }
}
onMounted(load)
</script>

<template>
  <section><h2>协作空间</h2><p>同一工作空间的成员可编辑项目；项目角色用于标明负责人和分工。</p>
    <div class="grid"><div class="panel"><h3>项目成员</h3><div v-for="member in members" :key="member.username" class="row"><span>{{ member.username }} <small>{{ member.role }}</small></span><button v-if="owner && member.username !== store.currentProject?.created_by" @click="remove(member.username)">移除</button></div>
      <div v-if="owner" class="form"><input v-model="username" placeholder="工作空间用户名" /><select v-model="role"><option>OWNER</option><option>EDITOR</option><option>VIEWER</option></select><button @click="invite">添加成员</button></div></div>
      <div class="panel"><h3>任务分配</h3><div v-for="item in assignments" :key="item.task_id + item.username" class="row"><span>{{ item.goal }} <small>→ {{ item.username }}</small></span></div><div class="form"><select v-model="taskId"><option value="">选择研究任务</option><option v-for="task in tasks" :key="task.task_id" :value="task.task_id">{{ task.goal }}</option></select><input v-model="assignee" placeholder="负责人用户名" /><button @click="assign">分配任务</button></div></div></div>
    <div class="panel comments"><h3>研究评论</h3><div class="form"><select v-model="targetType" @change="targetId='' "><option value="paper">论文</option><option value="claim">观点</option><option value="comparison">比较</option><option value="task">任务</option><option value="artifact">成果</option></select><select v-if="targetType !== 'artifact'" v-model="targetId"><option value="">选择对象</option><option v-for="target in targets" :key="target.id" :value="target.id">{{ target.name }}</option></select><input v-else v-model="targetId" placeholder="成果 ID" /><textarea v-model="comment" rows="2" placeholder="写下讨论内容" /><button @click="post">发表评论</button></div>
      <div v-for="item in comments" :key="item.comment_id" class="comment"><strong>{{ item.username }}</strong><small>{{ item.target_type }} · {{ item.target_id }} · {{ item.created_at ? new Date(item.created_at).toLocaleString() : '' }}</small><p>{{ item.content }}</p></div><p v-if="!comments.length">暂无评论。</p></div>
  </section>
</template>

<style scoped>.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.panel{background:white;border:1px solid #e0e6f0;border-radius:13px;padding:20px;margin:14px 0}.panel h3{margin-top:0}.row{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid #edf0f5}.row small{color:#6d5ec2}.row button{border:0;background:none;color:#a25f69;cursor:pointer}.form{display:flex;flex-wrap:wrap;gap:8px;margin-top:15px}.form input,.form select,.form textarea{min-width:160px;flex:1;border:1px solid #d8dfeb;border-radius:8px;padding:9px}.form textarea{flex-basis:100%}.form button{border:0;border-radius:8px;background:#5546b7;color:white;padding:9px 16px;cursor:pointer}.comment{border-top:1px solid #e8edf4;padding:13px 0}.comment small{display:block;color:#8390a0}.comment p{margin:5px 0}@media(max-width:850px){.grid{grid-template-columns:1fr}}</style>
