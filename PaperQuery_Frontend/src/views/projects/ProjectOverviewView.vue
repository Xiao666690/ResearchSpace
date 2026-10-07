<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { projectOverview } from '@/api/project'
const route = useRoute()
const overview = ref<any>(null)
onMounted(async () => { overview.value = await projectOverview(String(route.params.projectId)) })
</script>
<template>
  <section><h2>项目概览</h2><p>{{ overview?.project?.description || '为项目添加论文，开始构建研究脉络。' }}</p>
    <div class="stats"><div><b>{{ overview?.document_count ?? '—' }}</b><span>项目论文</span></div><div><b>{{ overview?.task_count ?? '—' }}</b><span>研究任务</span></div><div><b>{{ overview?.artifact_count ?? '—' }}</b><span>研究成果</span></div><div><b>{{ overview?.event_count ?? '—' }}</b><span>项目动态</span></div></div>
  </section>
</template>
<style scoped>.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:14px;margin-top:22px}.stats div{display:flex;flex-direction:column;padding:22px;background:white;border:1px solid #e2e7f1;border-radius:13px}.stats b{font-size:28px;color:#5546b7}.stats span{color:#677489}</style>
