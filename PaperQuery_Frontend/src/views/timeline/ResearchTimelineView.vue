<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { listTimeline, type TimelineEvent } from '@/api/timeline'
const route = useRoute()
const events = ref<TimelineEvent[]>([])
const loading = ref(true)
async function load() { loading.value = true; try { events.value = await listTimeline(String(route.params.projectId)) } finally { loading.value = false } }
onMounted(load)
const labels: Record<string,string> = { PROJECT_CREATED:'创建项目', PAPER_ADDED:'添加论文', PAPER_REMOVED:'移除论文', QUESTION_ASKED:'提出问题', TASK_CREATED:'创建任务', TASK_COMPLETED:'完成任务', TASK_FAILED:'任务失败', CLAIM_CREATED:'创建观点', EVIDENCE_ADDED:'加入证据', COMPARISON_CREATED:'完成比较', STUDIO_UPDATED:'编辑成果', COMMENT_CREATED:'添加评论', NOTE_UPDATED:'更新笔记' }
</script>
<template>
  <section><div class="heading"><h2>研究时间线</h2><button @click="load">刷新</button></div><p v-if="loading">正在加载…</p><p v-else-if="!events.length">项目还没有动态。</p>
    <ol v-else><li v-for="event in events" :key="event.id"><span class="dot" /><div><small>{{ new Date(event.created_at || '').toLocaleString() }}</small><h3>{{ labels[event.event_type] || event.event_type }}</h3><p>{{ event.title || event.description || '' }}</p></div></li></ol>
  </section>
</template>
<style scoped>.heading{display:flex;align-items:center;justify-content:space-between}.heading button{border:1px solid #d9dfee;border-radius:8px;background:white;padding:7px 14px;cursor:pointer}ol{padding:0;list-style:none}li{display:flex;gap:20px;border-left:1px solid #cfd6e4;margin-left:8px;padding:0 0 25px 20px;position:relative}.dot{position:absolute;left:-6px;top:4px;width:11px;height:11px;background:#6558bb;border-radius:50%}li div{background:white;border:1px solid #e1e6f0;padding:15px 20px;border-radius:11px;min-width:260px;max-width:650px}li small{color:#8490a1}li h3{margin:5px 0;font-size:15px}li p{margin:0;color:#5e6c80}</style>
