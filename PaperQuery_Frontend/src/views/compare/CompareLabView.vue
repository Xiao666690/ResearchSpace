<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createComparison, listComparisons, type Comparison } from '@/api/compare'
import { useResearchProjectStore } from '@/stores/researchProject'
const route = useRoute(), router = useRouter(), store = useResearchProjectStore()
const comparisons = ref<Comparison[]>([])
const question = ref('')
const columns = ref('方法,数据集,指标,局限')
const selected = ref<string[]>([])
const busy = ref(false)
async function load() { comparisons.value = await listComparisons(String(route.params.projectId)) }
async function create() {
  if (selected.value.length < 2) return ElMessage.warning('至少选择两篇项目论文')
  if (!question.value.trim()) return ElMessage.warning('请输入比较问题')
  busy.value = true
  try { const item = await createComparison(String(route.params.projectId), question.value,
    selected.value, columns.value.split(',').map(s => s.trim()).filter(Boolean)); comparisons.value.unshift(item); ElMessage.success('比较已生成') }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '比较失败') }
  finally { busy.value = false }
}
function source(cell: any) { if (cell?.citation) router.push({ name:'pdfInfo',params:{knowledgeID:cell.citation.knowledge_id,documentID:cell.citation.document_id},query:{page:cell.citation.page} }) }
onMounted(load)
</script>
<template>
  <section><h2>比较实验室</h2><p>逐项比较项目论文，核实每个单元格的原文依据。</p>
    <div class="setup"><input v-model="question" placeholder="想比较什么研究问题？" /><input v-model="columns" placeholder="比较维度，逗号分隔" />
      <div class="paper-options"><label v-for="paper in store.projectDocuments" :key="paper.document_id"><input v-model="selected" type="checkbox" :value="paper.document_id" /> {{ paper.document_name }}</label></div>
      <button :disabled="busy" @click="create">{{ busy ? '正在生成…' : '生成比较' }}</button></div>
    <p v-if="!comparisons.length">暂无比较结果。</p>
    <article v-for="comparison in comparisons" :key="comparison.session_id" class="result"><h3>{{ comparison.title }}</h3>
      <div class="table-wrap"><table><thead><tr><th>论文</th><th v-for="col in comparison.columns" :key="col">{{ col }}</th></tr></thead><tbody><tr v-for="row in comparison.rows" :key="row.document_id"><th>{{ row.paper }}</th><td v-for="col in comparison.columns" :key="col"><span>{{ row.cells[col]?.value || '未验证' }}</span><button v-if="row.cells[col]?.verified" @click="source(row.cells[col])">查看原文 · 第 {{ row.cells[col].citation?.page }} 页</button><small v-else>{{ row.cells[col]?.source_status === 'deleted' ? '来源已删除' : '未验证' }}</small></td></tr></tbody></table></div>
    </article>
  </section>
</template>
<style scoped>.setup,.result{background:white;border:1px solid #e1e7f0;border-radius:13px;padding:20px;margin:18px 0}.setup{display:grid;gap:12px;max-width:760px}.setup>input{border:1px solid #d8dfeb;border-radius:8px;padding:10px}.setup>button{justify-self:start;border:0;border-radius:8px;background:#5546b7;color:white;padding:10px 18px;cursor:pointer}.paper-options{display:grid;gap:7px}.table-wrap{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:600px}td,th{border:1px solid #dce3ef;padding:12px;text-align:left;vertical-align:top}thead th{background:#eef0fa}td button,td small{display:block;margin-top:7px;border:0;background:none;color:#6053b4;cursor:pointer;font-size:12px}td small{color:#9a7480}</style>
