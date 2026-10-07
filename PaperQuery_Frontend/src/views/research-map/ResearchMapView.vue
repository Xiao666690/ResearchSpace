<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import cytoscape from 'cytoscape'
import { buildGraph, getGraph, type GraphEdge, type GraphNode, type ResearchGraph } from '@/api/graph'

const route = useRoute(), router = useRouter()
const projectId = String(route.params.projectId)
const graph = ref<ResearchGraph | null>(null)
const canvas = ref<HTMLElement | null>(null)
const selected = ref<GraphNode | GraphEdge | null>(null)
const building = ref(false)
const typeFilter = ref('all')
let cy: cytoscape.Core | null = null
let timer: ReturnType<typeof setInterval> | null = null

async function load() {
  graph.value = await getGraph(projectId)
  building.value = graph.value.run?.status === 'PENDING' || graph.value.run?.status === 'RUNNING'
  await nextTick()
  draw()
  if (building.value && !timer) timer = setInterval(load, 2500)
  if (!building.value && timer) { clearInterval(timer); timer = null }
}
function draw() {
  if (!canvas.value || !graph.value) return
  cy?.destroy()
  const nodes = graph.value.nodes.filter(node => typeFilter.value === 'all' || node.type === typeFilter.value)
  const ids = new Set(nodes.map(node => node.id))
  cy = cytoscape({
    container: canvas.value,
    elements: [
      ...nodes.map(node => ({ data: { id: node.id, label: node.name, kind: node.type } })),
      ...graph.value.edges.filter(edge => ids.has(edge.source) && ids.has(edge.target))
        .map(edge => ({ data: { id: edge.id, source: edge.source, target: edge.target, label: edge.type } })),
    ],
    style: [
      { selector: 'node', style: { 'label': 'data(label)', 'background-color': '#6a5ac4',
        'color': '#27344f', 'font-size': '11px', 'text-wrap': 'wrap', 'text-max-width': '105px',
        'text-valign': 'bottom', 'text-margin-y': '8px', 'width': '26px', 'height': '26px' } },
      { selector: 'node[kind = "Paper"]', style: { 'background-color': '#263a6e', 'width': '38px', 'height': '38px' } },
      { selector: 'node[kind = "Claim"]', style: { 'background-color': '#c97b5a' } },
      { selector: 'edge', style: { 'width': 2, 'line-color': '#b9c3d7', 'target-arrow-color': '#b9c3d7',
        'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)',
        'font-size': '9px', 'color': '#728098' } },
      { selector: ':selected', style: { 'background-color': '#e0a54c', 'line-color': '#e0a54c' } },
    ],
    layout: { name: 'cose', animate: false, fit: true, padding: 45 },
  })
  cy.on('tap', 'node, edge', event => {
    const id = event.target.id()
    selected.value = graph.value?.nodes.find(node => node.id === id) || graph.value?.edges.find(edge => edge.id === id) || null
  })
}
async function startBuild() {
  try { await buildGraph(projectId); building.value = true; await load(); ElMessage.success('图谱构建已开始') }
  catch (error: any) { ElMessage.error(error?.response?.data?.detail || '构建失败') }
}
function openSource() {
  const citation = selected.value?.citation
  if (citation && selected.value?.source_status === 'available') router.push({ name:'pdfInfo',
    params:{knowledgeID:citation.knowledge_id,documentID:citation.document_id}, query:{page:citation.page} })
}
onMounted(load)
onBeforeUnmount(() => { if (timer) clearInterval(timer); cy?.destroy() })
</script>
<template>
  <section><div class="heading"><div><h2>研究图谱</h2><p>从已索引论文抽取方法、数据集、指标与原文主张。</p></div><button :disabled="building" @click="startBuild">{{ building ? '构建中…' : '构建研究图谱' }}</button></div>
    <p v-if="graph?.run?.status === 'FAILED'" class="error">构建失败：{{ graph.run.error }}。已有图谱仍可查看。</p>
    <div class="toolbar"><label>节点类型 <select v-model="typeFilter" @change="draw"><option value="all">全部</option><option v-for="type in ['Paper','Method','Dataset','Metric','Claim']" :key="type" :value="type">{{ type }}</option></select></label><span>{{ graph?.nodes.length || 0 }} 个节点 · {{ graph?.edges.length || 0 }} 条关系</span></div>
    <div class="map-layout"><div ref="canvas" class="canvas" aria-label="研究关系图" /><aside v-if="selected"><h3>{{ 'name' in selected ? selected.name : selected.type }}</h3><p>{{ 'name' in selected ? selected.type : '关系' }}</p><p>来源：{{ selected.source_status === 'available' ? `第 ${selected.citation.page} 页` : '来源已删除' }}</p><p>核验：{{ selected.confidence === 'source_matched' ? '原文匹配' : '待核验' }}</p><button v-if="selected.source_status === 'available'" @click="openSource">查看原文 →</button></aside></div>
    <p v-if="!building && !graph?.nodes.length">暂无图谱。添加并索引论文后点击“构建研究图谱”。</p>
  </section>
</template>
<style scoped>.heading{display:flex;align-items:center;justify-content:space-between;gap:15px}.heading button{border:0;border-radius:8px;background:#5546b7;color:white;padding:10px 16px;cursor:pointer}.heading button:disabled{opacity:.6}.toolbar{display:flex;gap:20px;align-items:center;color:#69788e;margin:20px 0}.toolbar select{padding:6px;border:1px solid #d8e0eb;border-radius:7px}.map-layout{display:flex;gap:14px}.canvas{width:100%;height:560px;background:white;border:1px solid #e1e7f0;border-radius:13px}.map-layout aside{width:250px;flex:none;background:white;border:1px solid #e1e7f0;border-radius:13px;padding:18px;overflow-wrap:anywhere}.map-layout aside button{border:0;background:none;color:#5546b7;cursor:pointer}.error{color:#b24e5b}@media(max-width:900px){.map-layout{flex-direction:column}.map-layout aside{width:auto}}</style>
