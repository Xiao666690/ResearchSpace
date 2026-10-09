<script setup lang="ts">
import FeatureHeader from '@/components/research/FeatureHeader.vue'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  createClaim,
  deleteClaim,
  listClaims,
  type Claim,
  type SavedEvidence,
} from '@/api/evidence'
const route = useRoute(),
  router = useRouter()
const filter = ref('all'),
  selectedEvidence = ref<SavedEvidence | null>(null),
  detailOpen = ref(false)
const filteredClaims = computed(() =>
  filter.value === 'all'
    ? claims.value
    : claims.value.filter((claim) =>
        claim.evidence.some((item) =>
          filter.value === 'support'
            ? item.stance === 'SUPPORT'
            : ['CONTRADICT', 'OPPOSE'].includes(item.stance),
        ),
      ),
)
function openDetail(item: SavedEvidence) {
  selectedEvidence.value = item
  detailOpen.value = true
}
const loading = ref(true),
  busy = ref(false),
  error = ref(''),
  deleting = ref('')
const stanceLabel = (stance: string) =>
  (
    ({
      SUPPORT: '支持证据',
      CONTRADICT: '反证',
      OPPOSE: '反证',
      NEUTRAL: '相关证据',
    }) as Record<string, string>
  )[stance] || stance
const claims = ref<Claim[]>([]),
  title = ref(''),
  content = ref('')
async function load() {
  loading.value = true
  error.value = ''
  try {
    claims.value = await listClaims(String(route.params.projectId))
  } catch {
    error.value = '证据加载失败，请重新加载。'
  } finally {
    loading.value = false
  }
}
async function create() {
  if (busy.value) return
  if (!title.value.trim() || !content.value.trim())
    return ElMessage.warning('请填写观点标题和内容')
  busy.value = true
  try {
    await createClaim(
      String(route.params.projectId),
      title.value,
      content.value,
    )
    title.value = ''
    content.value = ''
    await load()
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '保存失败')
  } finally {
    busy.value = false
  }
}
async function remove(id: string) {
  try {
    await ElMessageBox.confirm(
      '删除观点后，其关联的证据记录也会移除。原始论文仍会保留。',
      '删除研究观点',
      {
        confirmButtonText: '删除观点',
        cancelButtonText: '保留',
        type: 'warning',
      },
    )
  } catch {
    return
  }
  deleting.value = id
  try {
    await deleteClaim(String(route.params.projectId), id)
    await load()
    ElMessage.success('观点已删除')
  } catch {
    ElMessage.error('删除失败，请重试')
  } finally {
    deleting.value = ''
  }
}
function openSource(item: any) {
  if (item.source_status === 'available')
    router.push({
      name: 'pdfInfo',
      params: { knowledgeID: item.knowledge_id, documentID: item.document_id },
      query: { page: item.page_number },
    })
}
onMounted(load)
</script>
<template>
  <section class="rs-feature-page">
    <FeatureHeader
      eyebrow="REASONING / EVIDENCE"
      title="证据看板"
      description="每一个观点，都值得回到原文核对。将支持、反证与研究主张放在一起。"
      ><button @click="load">刷新证据</button></FeatureHeader
    >
    <div class="rs-summary-strip">
      <span
        ><b>{{ claims.length }}</b> 个研究观点</span
      ><span
        ><b>{{
          claims.reduce((total, claim) => total + claim.evidence.length, 0)
        }}</b>
        条原文依据</span
      >
    </div>
    <div class="evidence-filters" aria-label="证据类别">
      <button
        v-for="item in [
          ['all', '全部观点'],
          ['support', '有支持依据'],
          ['counter', '有反证依据'],
        ]"
        :key="item[0]"
        :class="{ active: filter === item[0] }"
        :aria-pressed="filter === item[0]"
        @click="filter = item[0]"
      >
        {{ item[1] }}
      </button>
    </div>
    <div class="create">
      <input
        v-model="title"
        aria-label="观点标题"
        placeholder="观点标题"
      /><textarea
        v-model="content"
        aria-label="观点内容"
        rows="3"
        placeholder="观点内容"
      /><button
        :disabled="busy || !title.trim() || !content.trim()"
        @click="create"
      >
        {{ busy ? '保存中…' : '＋ 保存观点' }}
      </button>
    </div>
    <p v-if="loading" class="rs-empty" aria-live="polite">正在整理研究证据…</p>
    <p v-else-if="error" class="rs-empty">{{ error }}</p>
    <p v-else-if="!claims.length" class="rs-empty">
      暂无观点，可从项目问答中的引用保存证据。
    </p>
    <article
      v-for="claim in filteredClaims"
      :key="claim.claim_id"
      class="claim"
    >
      <div class="heading">
        <h3>{{ claim.title }}</h3>
        <button
          :disabled="deleting === claim.claim_id"
          @click="remove(claim.claim_id)"
        >
          {{ deleting === claim.claim_id ? '删除中…' : '删除观点' }}
        </button>
      </div>
      <p>{{ claim.content }}</p>
      <div
        v-for="item in claim.evidence"
        :key="item.evidence_id"
        class="evidence"
      >
        <small
          >{{ stanceLabel(item.stance) }} ·
          {{
            item.source_status === 'deleted'
              ? '来源已删除'
              : `第 ${item.page_number} 页`
          }}</small
        ><button class="evidence-detail" @click="openDetail(item)">
          <span>{{ item.text }}</span
          ><em>展开证据 ↗</em></button
        ><button
          v-if="item.source_status === 'available'"
          @click="openSource(item)"
        >
          查看原文 →
        </button>
      </div>
      <small v-if="!claim.evidence.length">尚无可核对的引用</small>
    </article>
    <p
      v-if="!loading && claims.length && !filteredClaims.length"
      class="rs-empty"
    >
      这一类别暂时没有证据。将问答中的原文引用保存到观点后，在这里核对。
    </p>
    <el-dialog
      v-model="detailOpen"
      title="原文证据"
      width="min(640px, calc(100vw - 32px))"
      ><div v-if="selectedEvidence" class="evidence-inspector">
        <p class="library-kicker">
          {{ stanceLabel(selectedEvidence.stance) }} / SOURCE
        </p>
        <blockquote>{{ selectedEvidence.text }}</blockquote>
        <p>
          {{
            selectedEvidence.source_status === 'available'
              ? `原文第 ${selectedEvidence.page_number} 页`
              : '原文来源已删除，这段证据仍保留供核对。'
          }}
        </p>
        <button
          v-if="selectedEvidence.source_status === 'available'"
          @click="openSource(selectedEvidence)"
        >
          前往原文核对 ↗
        </button>
      </div></el-dialog
    >
  </section>
</template>
<style scoped>
.rs-feature-page {
  min-width: 0;
  overflow-wrap: anywhere;
}
.heading {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.heading button,
.claim button {
  border: 0;
  background: none;
  color: #6558b7;
  cursor: pointer;
}
.create,
.claim {
  background: white;
  border: 1px solid #e2e7f0;
  border-radius: 13px;
  padding: 20px;
  margin: 18px 0;
}
.create {
  display: grid;
  gap: 10px;
  max-width: 700px;
}
.create input,
.create textarea {
  border: 1px solid #d8e0ec;
  border-radius: 8px;
  padding: 10px;
}
.create button {
  justify-self: start;
  background: #5546b7;
  color: white;
  border: 0;
  border-radius: 8px;
  padding: 10px 20px;
  cursor: pointer;
}
.claim h3 {
  margin: 0;
}
.claim > p {
  color: #4a5870;
}
.evidence {
  border-left: 3px solid #7468c5;
  background: #f5f6fb;
  padding: 12px 15px;
  margin: 10px 0;
}
.evidence small {
  color: #6a5fb5;
}
.evidence p {
  margin: 7px 0;
  color: #40506a;
}
.evidence-filters {
  display: flex;
  gap: 6px;
  margin-top: 20px;
  flex-wrap: wrap;
}
.evidence-filters button {
  padding: 8px 12px;
  border: 1px solid var(--rs-line);
  border-radius: 8px;
  color: var(--rs-muted);
  background: white;
}
.evidence-filters button.active {
  background: #efedf9;
  color: var(--rs-primary);
  border-color: #d9d2ee;
}
.evidence .evidence-detail {
  width: 100%;
  text-align: left;
  color: var(--rs-ink);
  padding: 0;
  margin: 9px 0 12px;
}
.evidence-detail span {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  font-size: 13px;
  line-height: 1.8;
}
.evidence-detail em {
  display: block;
  font-size: 11px;
  font-style: normal;
  color: var(--rs-primary);
  margin-top: 8px;
}
.evidence-inspector blockquote {
  border-left: 2px solid var(--rs-primary);
  padding: 16px 20px;
  background: #f6f4fa;
  font-size: 15px;
  line-height: 1.9;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  margin: 16px 0;
}
.evidence-inspector > p {
  font-size: 12px;
  color: var(--rs-muted);
}
.evidence-inspector button {
  padding: 10px 16px;
  border: 0;
  border-radius: 8px;
  background: var(--rs-primary);
  color: white;
}
</style>
