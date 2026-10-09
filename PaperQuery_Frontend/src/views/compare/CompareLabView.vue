<script setup lang="ts">
import FeatureHeader from '@/components/research/FeatureHeader.vue'
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  createComparison,
  listComparisons,
  type Comparison,
} from '@/api/compare'
import { useResearchProjectStore } from '@/stores/researchProject'
const route = useRoute(),
  router = useRouter(),
  store = useResearchProjectStore()
const comparisons = ref<Comparison[]>([])
const question = ref('')
const columns = ref('方法,数据集,指标,局限')
const selected = ref<string[]>([])
const busy = ref(false),
  loading = ref(true),
  error = ref(''),
  detailOpen = ref(false),
  selectedCell = ref<any>(null)
function inspect(cell: any, paper: string, dimension: string) {
  selectedCell.value = { ...cell, paper, dimension }
  detailOpen.value = true
}
async function load() {
  loading.value = true
  error.value = ''
  try {
    comparisons.value = await listComparisons(String(route.params.projectId))
  } catch {
    error.value = '比较结果暂时无法加载，请重试。'
  } finally {
    loading.value = false
  }
}
async function create() {
  if (selected.value.length < 2)
    return ElMessage.warning('至少选择两篇项目论文')
  if (!question.value.trim()) return ElMessage.warning('请输入比较问题')
  busy.value = true
  try {
    const item = await createComparison(
      String(route.params.projectId),
      question.value,
      selected.value,
      columns.value
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean),
    )
    comparisons.value.unshift(item)
    ElMessage.success('比较已生成')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '比较失败')
  } finally {
    busy.value = false
  }
}
function source(cell: any) {
  if (cell?.citation)
    router.push({
      name: 'pdfInfo',
      params: {
        knowledgeID: cell.citation.knowledge_id,
        documentID: cell.citation.document_id,
      },
      query: { page: cell.citation.page },
    })
}
onMounted(load)
</script>
<template>
  <section class="rs-feature-page">
    <FeatureHeader
      eyebrow="ANALYSIS / COMPARISON"
      title="比较实验室"
      description="从同一个问题出发，并列审视方法、数据和局限。"
    />
    <div class="setup">
      <label class="setup-label"
        >比较问题<input
          v-model="question"
          aria-label="比较问题"
          placeholder="想比较什么研究问题？" /></label
      ><label class="setup-label"
        >比较维度<input
          v-model="columns"
          aria-label="比较维度"
          placeholder="比较维度，逗号分隔" /></label
      ><small>已选择 {{ selected.length }} 篇论文 · 至少选择两篇</small>
      <p v-if="!store.projectDocuments.length" class="rs-empty">
        项目内暂无论文，请先从“论文”页加入资料。
      </p>
      <div class="paper-options">
        <label v-for="paper in store.projectDocuments" :key="paper.document_id"
          ><input
            v-model="selected"
            type="checkbox"
            :value="paper.document_id"
          />
          {{ paper.document_name }}</label
        >
      </div>
      <button
        :disabled="busy || selected.length < 2 || !question.trim()"
        @click="create"
      >
        {{ busy ? '正在生成…' : '生成比较' }}
      </button>
    </div>
    <p v-if="loading" class="rs-empty" aria-live="polite">正在加载比较结果…</p>
    <p v-else-if="error" class="rs-empty">
      {{ error }} <button @click="load">重试</button>
    </p>
    <p v-else-if="!comparisons.length" class="rs-empty">暂无比较结果。</p>
    <article
      v-for="comparison in comparisons"
      :key="comparison.session_id"
      class="result"
    >
      <h3>{{ comparison.title }}</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>论文</th>
              <th v-for="col in comparison.columns" :key="col">{{ col }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in comparison.rows" :key="row.document_id">
              <th>{{ row.paper }}</th>
              <td v-for="col in comparison.columns" :key="col">
                <button
                  class="cell-inspect"
                  @click="inspect(row.cells[col], row.paper, col)"
                >
                  {{ row.cells[col]?.value || '未验证'
                  }}<em>展开详情 ↗</em></button
                ><button
                  v-if="row.cells[col]?.verified"
                  @click="source(row.cells[col])"
                >
                  查看原文 · 第 {{ row.cells[col].citation?.page }} 页</button
                ><small v-else>{{
                  row.cells[col]?.source_status === 'deleted'
                    ? '来源已删除'
                    : '未验证'
                }}</small>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>
    <el-dialog
      v-model="detailOpen"
      title="比较单元格"
      width="min(620px, calc(100vw - 32px))"
      ><div v-if="selectedCell" class="cell-detail">
        <p class="library-kicker">{{ selectedCell.dimension }}</p>
        <h3>{{ selectedCell.paper }}</h3>
        <p>{{ selectedCell.value || '暂无可核验的内容。' }}</p>
        <button
          v-if="selectedCell.verified && selectedCell.citation"
          @click="source(selectedCell)"
        >
          核对原文 · 第 {{ selectedCell.citation.page }} 页 ↗</button
        ><small v-else>{{
          selectedCell.source_status === 'deleted'
            ? '来源已删除'
            : '这一结论尚未核验，请谨慎引用。'
        }}</small>
      </div></el-dialog
    >
  </section>
</template>
<style scoped>
.rs-feature-page {
  min-width: 0;
  overflow-wrap: anywhere;
}
.setup,
.result {
  background: white;
  border: 1px solid #e1e7f0;
  border-radius: 13px;
  padding: 20px;
  margin: 18px 0;
}
.setup {
  display: grid;
  gap: 12px;
  max-width: 760px;
}
.setup > input {
  border: 1px solid #d8dfeb;
  border-radius: 8px;
  padding: 10px;
}
.setup > button {
  justify-self: start;
  border: 0;
  border-radius: 8px;
  background: #5546b7;
  color: white;
  padding: 10px 18px;
  cursor: pointer;
}
.paper-options {
  display: grid;
  gap: 7px;
}
.table-wrap {
  overflow-x: auto;
}
table {
  border-collapse: collapse;
  width: 100%;
  min-width: 600px;
}
td,
th {
  border: 1px solid #dce3ef;
  padding: 12px;
  text-align: left;
  vertical-align: top;
}
thead th {
  background: #eef0fa;
}
td button,
td small {
  display: block;
  margin-top: 7px;
  border: 0;
  background: none;
  color: #6053b4;
  cursor: pointer;
  font-size: 12px;
}
td small {
  color: #9a7480;
}
.setup-label {
  display: grid;
  gap: 8px;
  font-size: 12px;
  color: var(--rs-muted);
}
.setup-label input {
  border: 1px solid var(--rs-line);
  border-radius: 8px;
  padding: 10px;
}
.setup > small {
  font-size: 12px;
  color: var(--rs-muted);
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
.cell-inspect {
  padding: 0;
  text-align: left !important;
  color: var(--rs-ink) !important;
  font-size: 13px !important;
  margin: 0 !important;
  line-height: 1.8;
}
.cell-inspect em {
  display: block;
  font-size: 10px;
  font-style: normal;
  color: var(--rs-primary);
  margin-top: 9px;
}
.cell-detail h3 {
  font-size: 20px;
  line-height: 1.6;
  overflow-wrap: anywhere;
}
.cell-detail p {
  font-size: 14px;
  line-height: 1.9;
  white-space: pre-wrap;
}
.cell-detail button {
  border: 0;
  padding: 10px 15px;
  border-radius: 8px;
  background: var(--rs-primary);
  color: #fff;
}
.cell-detail small {
  font-size: 12px;
  color: var(--rs-muted);
}
.table-wrap tbody th,
.table-wrap thead th:first-child {
  position: sticky;
  left: 0;
  background: #fbfbf8;
  z-index: 1;
}
</style>
