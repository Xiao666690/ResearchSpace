<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { addProjectDocument, removeProjectDocument } from '@/api/project'
import { getKnowledgeList, getDocumentList } from '@/api/data'
import { useResearchProjectStore } from '@/stores/researchProject'
const route = useRoute()
const store = useResearchProjectStore()
const libraries = ref<any[]>([])
const candidates = ref<any[]>([])
const selectedLibrary = ref('')
const selectedPaper = ref('')
async function loadLibraries() { libraries.value = (await getKnowledgeList()).data?.knowledgeList || [] }
async function loadCandidates() { candidates.value = selectedLibrary.value ? (await getDocumentList(selectedLibrary.value)).data || [] : [] }
async function add() {
  if (!selectedLibrary.value || !selectedPaper.value) return
  try { await addProjectDocument(String(route.params.projectId), selectedLibrary.value, selectedPaper.value); await store.loadProjectDocuments(); ElMessage.success('已加入项目') }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '添加失败') }
}
async function remove(knowledgeId: string, documentId: string) {
  await removeProjectDocument(String(route.params.projectId), knowledgeId, documentId)
  await store.loadProjectDocuments()
}
onMounted(loadLibraries)
</script>
<template>
  <section><h2>项目论文</h2><p>从工作空间论文库引用论文，不会移动原文件。</p>
    <div class="picker"><select v-model="selectedLibrary" @change="loadCandidates"><option value="">选择知识库</option><option v-for="library in libraries" :key="library.knowledgeID" :value="library.knowledgeID">{{ library.knowledgeName }}</option></select>
      <select v-model="selectedPaper"><option value="">选择论文</option><option v-for="paper in candidates" :key="paper.documentID" :value="paper.documentID">{{ paper.documentName }}</option></select><button @click="add">添加论文</button></div>
    <div v-if="!store.projectDocuments.length" class="empty">项目内还没有论文。</div>
    <article v-for="paper in store.projectDocuments" :key="paper.knowledge_id + paper.document_id" class="paper">
      <div><strong>{{ paper.document_name }}</strong><small>{{ paper.document_status === 1 ? '已索引' : '处理中' }}</small></div>
      <div><router-link :to="{name:'pdfInfo',params:{knowledgeID:paper.knowledge_id,documentID:paper.document_id}}">查看原文</router-link><button @click="remove(paper.knowledge_id,paper.document_id)">移除</button></div>
    </article>
  </section>
</template>
<style scoped>.picker{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}.picker select,.picker button{padding:10px;border:1px solid #dce1ec;border-radius:8px;background:white}.picker button{background:#5546b7;color:white;cursor:pointer}.paper{display:flex;justify-content:space-between;gap:15px;align-items:center;background:white;border:1px solid #e2e7f1;border-radius:10px;padding:15px;margin:9px 0}.paper div{display:flex;gap:15px;align-items:center}.paper small{color:#8793a3}.paper a{color:#5546b7}.paper button{border:0;background:none;color:#8e6470;cursor:pointer}.empty{padding:28px;color:#8090a0}</style>
