<script setup lang="ts">
import FeatureHeader from '@/components/research/FeatureHeader.vue'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { addProjectDocument, removeProjectDocument } from '@/api/project'
import { getKnowledgeList, getDocumentList } from '@/api/data'
import { useResearchProjectStore } from '@/stores/researchProject'
const route = useRoute()
const store = useResearchProjectStore()
const loading = ref(true),
  error = ref('')
const libraries = ref<any[]>([])
const candidates = ref<any[]>([])
const busy = ref(false),
  removing = ref('')
const selectedLibrary = ref('')
const selectedPaper = ref('')
async function loadLibraries() {
  loading.value = true
  error.value = ''
  try {
    libraries.value = (await getKnowledgeList()).data?.knowledgeList || []
  } catch {
    error.value = '知识库列表加载失败。'
  } finally {
    loading.value = false
  }
}
async function loadCandidates() {
  selectedPaper.value = ''
  candidates.value = []
  if (!selectedLibrary.value) return
  try {
    candidates.value = (await getDocumentList(selectedLibrary.value)).data || []
  } catch {
    ElMessage.error('论文列表加载失败，请重新选择知识库。')
  }
}
async function add() {
  if (busy.value || !selectedLibrary.value || !selectedPaper.value) return
  busy.value = true
  try {
    await addProjectDocument(
      String(route.params.projectId),
      selectedLibrary.value,
      selectedPaper.value,
    )
    await store.loadProjectDocuments()
    ElMessage.success('已加入项目')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '添加失败')
  } finally {
    busy.value = false
  }
}
async function remove(knowledgeId: string, documentId: string) {
  removing.value = documentId
  try {
    await removeProjectDocument(
      String(route.params.projectId),
      knowledgeId,
      documentId,
    )
    await store.loadProjectDocuments()
  } catch {
    ElMessage.error('论文移除失败')
  } finally {
    removing.value = ''
  }
}
onMounted(loadLibraries)
</script>
<template>
  <section class="rs-feature-page">
    <FeatureHeader
      eyebrow="ARCHIVE / PAPERS"
      title="项目论文"
      description="让论文成为研究的基础。从工作空间引用资料，原文件始终保留。"
    />
    <p v-if="error" class="rs-empty">
      {{ error }} <button @click="loadLibraries">重试</button>
    </p>
    <div class="picker">
      <select
        aria-label="选择知识库"
        :disabled="loading"
        v-model="selectedLibrary"
        @change="loadCandidates"
      >
        <option value="">选择知识库</option>
        <option
          v-for="library in libraries"
          :key="library.knowledgeID"
          :value="library.knowledgeID"
        >
          {{ library.knowledgeName }}
        </option>
      </select>
      <select
        aria-label="选择论文"
        :disabled="!selectedLibrary"
        v-model="selectedPaper"
      >
        <option value="">选择论文</option>
        <option
          v-for="paper in candidates"
          :key="paper.documentID"
          :value="paper.documentID"
        >
          {{ paper.documentName }}
        </option></select
      ><button
        :disabled="busy || !selectedPaper || !selectedLibrary"
        @click="add"
      >
        {{ busy ? '添加中…' : '加入项目' }}
      </button>
    </div>
    <div v-if="!store.projectDocuments.length" class="empty rs-empty">
      项目内还没有论文。
    </div>
    <article
      v-for="paper in store.projectDocuments"
      :key="paper.knowledge_id + paper.document_id"
      class="paper"
    >
      <div>
        <strong>{{ paper.document_name }}</strong
        ><small>{{ paper.document_status === 2 ? '已索引' : '处理中' }}</small>
      </div>
      <div>
        <router-link
          :to="{
            name: 'pdfInfo',
            params: {
              knowledgeID: paper.knowledge_id,
              documentID: paper.document_id,
            },
          }"
          >查看原文</router-link
        ><button
          :disabled="removing === paper.document_id"
          @click="remove(paper.knowledge_id, paper.document_id)"
        >
          {{ removing === paper.document_id ? '移除中…' : '移除' }}
        </button>
      </div>
    </article>
  </section>
</template>
<style scoped>
.rs-feature-page {
  min-width: 0;
  overflow-wrap: anywhere;
}
.picker {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin: 20px 0;
}
.picker select,
.picker button {
  padding: 10px;
  border: 1px solid #dce1ec;
  border-radius: 8px;
  background: white;
}
.picker button {
  background: #5546b7;
  color: white;
  cursor: pointer;
}
.paper {
  display: flex;
  justify-content: space-between;
  gap: 15px;
  align-items: center;
  background: white;
  border: 1px solid #e2e7f1;
  border-radius: 10px;
  padding: 15px;
  margin: 9px 0;
}
.paper div {
  display: flex;
  gap: 15px;
  align-items: center;
}
.paper small {
  color: #8793a3;
}
.paper a {
  color: #5546b7;
}
.paper button {
  border: 0;
  background: none;
  color: #8e6470;
  cursor: pointer;
}
.empty {
  padding: 28px;
  color: #8090a0;
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
