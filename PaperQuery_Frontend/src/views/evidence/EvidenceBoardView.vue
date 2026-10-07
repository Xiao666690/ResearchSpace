<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { createClaim, deleteClaim, listClaims, type Claim } from '@/api/evidence'
const route = useRoute(), router = useRouter()
const claims = ref<Claim[]>([]), title = ref(''), content = ref('')
async function load() { claims.value = await listClaims(String(route.params.projectId)) }
async function create() {
  if (!title.value.trim() || !content.value.trim()) return ElMessage.warning('请填写观点标题和内容')
  try { await createClaim(String(route.params.projectId), title.value, content.value); title.value=''; content.value=''; await load() }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '保存失败') }
}
async function remove(id: string) { await deleteClaim(String(route.params.projectId), id); await load() }
function openSource(item: any) { if (item.source_status === 'available') router.push({name:'pdfInfo',params:{knowledgeID:item.knowledge_id,documentID:item.document_id},query:{page:item.page_number}}) }
onMounted(load)
</script>
<template>
  <section><div class="heading"><div><h2>证据看板</h2><p>把研究观点与原文依据放在一起。</p></div><button @click="load">刷新</button></div>
    <div class="create"><input v-model="title" placeholder="观点标题" /><textarea v-model="content" rows="3" placeholder="观点内容" /><button @click="create">保存观点</button></div>
    <p v-if="!claims.length">暂无观点，可从项目问答中的引用保存证据。</p>
    <article v-for="claim in claims" :key="claim.claim_id" class="claim"><div class="heading"><h3>{{ claim.title }}</h3><button @click="remove(claim.claim_id)">删除</button></div><p>{{ claim.content }}</p>
      <div v-for="item in claim.evidence" :key="item.evidence_id" class="evidence"><small>{{ item.stance }} · {{ item.source_status === 'deleted' ? '来源已删除' : `第 ${item.page_number} 页` }}</small><p>{{ item.text }}</p><button v-if="item.source_status === 'available'" @click="openSource(item)">查看原文 →</button></div>
      <small v-if="!claim.evidence.length">尚无可核对的引用</small>
    </article>
  </section>
</template>
<style scoped>.heading{display:flex;justify-content:space-between;align-items:center}.heading button,.claim button{border:0;background:none;color:#6558b7;cursor:pointer}.create,.claim{background:white;border:1px solid #e2e7f0;border-radius:13px;padding:20px;margin:18px 0}.create{display:grid;gap:10px;max-width:700px}.create input,.create textarea{border:1px solid #d8e0ec;border-radius:8px;padding:10px}.create button{justify-self:start;background:#5546b7;color:white;border:0;border-radius:8px;padding:10px 20px;cursor:pointer}.claim h3{margin:0}.claim>p{color:#4a5870}.evidence{border-left:3px solid #7468c5;background:#f5f6fb;padding:12px 15px;margin:10px 0}.evidence small{color:#6a5fb5}.evidence p{margin:7px 0;color:#40506a}</style>
