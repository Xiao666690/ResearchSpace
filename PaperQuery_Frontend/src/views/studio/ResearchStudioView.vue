<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { addStudioCitation, createStudio, listStudio, updateStudio, type StudioDocument } from '@/api/studio'
import { listClaims, type Claim } from '@/api/evidence'
const route = useRoute(), router = useRouter()
const items = ref<StudioDocument[]>([])
const current = ref<StudioDocument | null>(null)
const title = ref(''), content = ref(''), busy = ref(false)
const claims = ref<Claim[]>([]), evidenceId = ref(''), citationKey = ref('C1')
const availableEvidence = computed(() => claims.value.flatMap(claim => claim.evidence
  .filter(item => item.source_status === 'available')
  .map(item => ({ ...item, title: claim.title }))))
const projectId = String(route.params.projectId)
async function load() {
  items.value = await listStudio(projectId)
  const selected = items.value.find(item => item.studio_id === route.query.document)
  if (selected) select(selected)
  else if (!current.value && items.value.length) select(items.value[0])
}
function select(item: StudioDocument) { current.value = item; title.value = item.title; content.value = item.content_markdown; router.replace({ query: { document: item.studio_id } }) }
async function create() { const item = await createStudio(projectId, '未命名研究文稿'); items.value.unshift(item); select(item) }
async function save() {
  if (!current.value) return
  busy.value = true
  try { const updated = await updateStudio(projectId, current.value.studio_id, title.value, content.value); current.value = updated; const index = items.value.findIndex(item => item.studio_id === updated.studio_id); if (index >= 0) items.value[index] = updated; ElMessage.success('已保存') }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '保存失败') }
  finally { busy.value = false }
}
async function insertCitation() {
  if (!current.value) return
  const evidence = availableEvidence.value.find(item => item.evidence_id === evidenceId.value)
  if (!evidence) return ElMessage.warning('请选择证据看板中的原文证据')
  try {
    current.value = await addStudioCitation(projectId, current.value.studio_id, {
      citation_key: citationKey.value, knowledge_id: evidence.knowledge_id,
      document_id: evidence.document_id, page_number: evidence.page_number, chunk_id: evidence.chunk_id,
    })
    content.value += `\n[C${citationKey.value.replace(/^C/, '')}]`
    ElMessage.success('引用已核验；请保存文稿内容')
  } catch (error: any) { ElMessage.error(error?.response?.data?.detail || '引用失败') }
}
function openSource(citation: StudioDocument['citations'][number]) {
  if (citation.source_status === 'available') router.push({name:'pdfInfo',params:{knowledgeID:citation.knowledge_id,documentID:citation.document_id},query:{page:citation.page}})
}
onMounted(async () => { await load(); claims.value = await listClaims(projectId) })
</script>

<template>
  <section><div class="heading"><h2>成果工作室</h2><button @click="create">新建文稿</button></div><p>编辑研究报告和导入的成果；引用需在原文核验后添加。</p>
    <div class="workspace"><aside><button v-for="item in items" :key="item.studio_id" :class="{active:item.studio_id===current?.studio_id}" @click="select(item)">{{ item.title }}</button><small v-if="!items.length">暂无文稿</small></aside>
      <div v-if="current" class="editor"><div class="bar"><input v-model="title" maxlength="255" aria-label="文稿标题" /><button :disabled="busy" @click="save">{{ busy ? '保存中…' : '保存文稿' }}</button></div>
        <MdEditor v-model="content" language="zh-CN" :preview="true" style="height: 560px" />
        <h3>已核验引用</h3><p v-if="!current.citations.length">当前文稿尚无已核验引用。</p>
        <div class="citation-form"><input v-model="citationKey" placeholder="引用编号，如 C1" /><select v-model="evidenceId"><option value="">从证据看板选择原文</option><option v-for="item in availableEvidence" :key="item.evidence_id" :value="item.evidence_id">{{ item.title }} · 第 {{ item.page_number }} 页</option></select><button @click="insertCitation">加入引用</button></div>
        <div v-for="citation in current.citations" :key="citation.citation_key" class="citation"><strong>[{{ citation.citation_key }}]</strong><span>{{ citation.source_status === 'deleted' ? '来源已删除' : `原文第 ${citation.page} 页` }}</span><button v-if="citation.source_status === 'available'" @click="openSource(citation)">查看原文</button></div>
      </div><div v-else class="empty">新建文稿或从研究任务导入成果。</div></div>
  </section>
</template>

<style scoped>.heading{display:flex;justify-content:space-between;align-items:center}.heading button,.bar button{background:#5546b7;color:white;border:0;border-radius:8px;padding:9px 16px;cursor:pointer}.workspace{display:grid;grid-template-columns:220px minmax(0,1fr);gap:16px;margin-top:20px}.workspace aside{background:white;border:1px solid #e1e6f0;border-radius:11px;padding:10px;min-height:300px}.workspace aside button{display:block;width:100%;text-align:left;padding:11px;border:0;background:white;border-radius:8px;cursor:pointer}.workspace aside button.active{background:#f0effb;color:#5546b7;font-weight:600}.editor{min-width:0}.bar{display:flex;gap:12px;margin-bottom:12px}.bar input{flex:1;border:1px solid #d7deea;border-radius:8px;padding:9px;font-size:17px}.citation-form{display:flex;gap:8px;flex-wrap:wrap}.citation-form input,.citation-form select{border:1px solid #d7deea;border-radius:7px;padding:7px}.citation-form button{background:#5546b7;color:white;border:0;border-radius:7px;padding:7px 12px;cursor:pointer}.citation{display:flex;gap:14px;padding:8px;border-bottom:1px solid #e5e8ee}.citation button{border:0;background:none;color:#5546b7;cursor:pointer}.empty{color:#8290a0;padding:25px}@media(max-width:800px){.workspace{grid-template-columns:1fr}.workspace aside{min-height:auto}}</style>
