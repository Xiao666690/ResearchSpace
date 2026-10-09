<script setup lang="ts">
import FeatureHeader from '@/components/research/FeatureHeader.vue'
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import cytoscape from 'cytoscape'
import {
  buildGraph,
  getGraph,
  type GraphEdge,
  type GraphNode,
  type ResearchGraph,
} from '@/api/graph'

const route = useRoute(),
  router = useRouter()
const projectId = String(route.params.projectId)
const graph = ref<ResearchGraph | null>(null)
const canvas = ref<HTMLElement | null>(null)
const selected = ref<GraphNode | GraphEdge | null>(null)
const building = ref(false)
const typeFilter = ref('all')
const error = ref('')
function zoom(amount: number) {
  if (!cy) return
  const level = Math.max(0.15, Math.min(3, cy.zoom() + amount))
  cy.zoom({
    level,
    renderedPosition: { x: cy.width() / 2, y: cy.height() / 2 },
  })
}
function fit() {
  if(!cy) return
  cy.fit(undefined, 45)
  if(cy.zoom() > 1.25){cy.zoom(1.25);cy.center()}
}
let cy: cytoscape.Core | null = null
let timer: ReturnType<typeof setInterval> | null = null

async function load() {
  try {
    graph.value = await getGraph(projectId)
    error.value = ''
  } catch {
    error.value = '图谱暂时无法加载，请稍后重试。'
    return
  }
  building.value =
    graph.value.run?.status === 'PENDING' ||
    graph.value.run?.status === 'RUNNING'
  await nextTick()
  draw()
  if (building.value && !timer) timer = setInterval(load, 2500)
  if (!building.value && timer) {
    clearInterval(timer)
    timer = null
  }
}
function draw() {
  if (!canvas.value || !graph.value) return
  const previousZoom = cy?.zoom(),
    previousPan = cy?.pan()
  const previousPositions = new Map<string, cytoscape.Position>()
  cy?.nodes().forEach((node) => {
    previousPositions.set(node.id(), { ...node.position() })
  })
  cy?.destroy()
  const nodes = graph.value.nodes.filter(
    (node) => typeFilter.value === 'all' || node.type === typeFilter.value,
  )
  const ids = new Set(nodes.map((node) => node.id))
  cy = cytoscape({
    container: canvas.value,
    minZoom: 0.15,
    maxZoom: 3,
    elements: [
      ...nodes.map((node) => ({
        data: { id: node.id, label: node.name, kind: node.type },
      })),
      ...graph.value.edges
        .filter((edge) => ids.has(edge.source) && ids.has(edge.target))
        .map((edge) => ({
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            label: edge.type,
          },
        })),
    ],
    style: [
      {
        selector: 'node',
        style: {
          label: 'data(label)',
          'background-color': '#6a5ac4',
          color: '#27344f',
          'font-size': '11px',
          'text-wrap': 'wrap',
          'text-max-width': '105px',
          'text-valign': 'bottom',
          'text-margin-y': '8px',
          width: '26px',
          height: '26px',
        },
      },
      {
        selector: 'node[kind = "Paper"]',
        style: { 'background-color': '#263a6e', width: '38px', height: '38px' },
      },
      {
        selector: 'node[kind = "Claim"]',
        style: { 'background-color': '#c97b5a' },
      },
      {
        selector: 'edge',
        style: {
          width: 2,
          'line-color': '#b9c3d7',
          'target-arrow-color': '#b9c3d7',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          label: 'data(label)',
          'font-size': '9px',
          color: '#728098',
        },
      },
      {
        selector: ':selected',
        style: { 'background-color': '#e0a54c', 'line-color': '#e0a54c' },
      },
    ],
    layout: { name: 'cose', animate: false, fit: true, padding: 45 },
  })
  if(previousZoom === undefined) fit()
  cy.nodes().forEach((node) => {
    const position = previousPositions.get(node.id())
    if (position) node.position(position)
  })
  if (previousZoom !== undefined && previousPan) {
    cy.zoom(previousZoom)
    cy.pan(previousPan)
  }
  cy.on('tap', 'node, edge', (event) => {
    const id = event.target.id()
    selected.value =
      graph.value?.nodes.find((node) => node.id === id) ||
      graph.value?.edges.find((edge) => edge.id === id) ||
      null
  })
}
async function startBuild() {
  if (building.value) return
  building.value = true
  try {
    await buildGraph(projectId)
    building.value = true
    await load()
    ElMessage.success('图谱构建已开始')
  } catch (error: any) {
    ElMessage.error(error?.response?.data?.detail || '构建失败')
    building.value = false
  }
}
function openSource() {
  const citation = selected.value?.citation
  if (citation && selected.value?.source_status === 'available')
    router.push({
      name: 'pdfInfo',
      params: {
        knowledgeID: citation.knowledge_id,
        documentID: citation.document_id,
      },
      query: { page: citation.page },
    })
}
onMounted(load)
onBeforeUnmount(() => {
  if (timer) clearInterval(timer)
  cy?.destroy()
})
</script>
<template>
  <section class="rs-feature-page">
    <FeatureHeader
      eyebrow="DISCOVERY / MAP"
      title="研究图谱"
      description="探索论文之间的方法、数据集、指标和主张。点击节点核对原文。"
      ><button :disabled="building" @click="startBuild">
        {{ building ? '构建中…' : '构建研究图谱' }}
      </button></FeatureHeader
    >
    <p v-if="error" class="rs-empty">
      {{ error }} <button @click="load">重新加载</button>
    </p>
    <p v-if="graph?.run?.status === 'FAILED'" class="error">
      构建失败：{{ graph.run.error }}。已有图谱仍可查看。
    </p>
    <div class="toolbar">
      <label
        >节点类型
        <select aria-label="节点类型" v-model="typeFilter" @change="draw">
          <option value="all">全部</option>
          <option
            v-for="type in ['Paper', 'Method', 'Dataset', 'Metric', 'Claim']"
            :key="type"
            :value="type"
          >
            {{ type }}
          </option>
        </select></label
      ><span
        >{{ graph?.nodes.length || 0 }} 个节点 ·
        {{ graph?.edges.length || 0 }} 条关系</span
      >
      <div class="map-controls">
        <button aria-label="缩小图谱" @click="zoom(-0.2)">−</button
        ><button aria-label="放大图谱" @click="zoom(0.2)">＋</button
        ><button @click="fit">适应画布</button>
      </div>
    </div>
    <div class="map-legend">
      <span><i style="background: #263a6e" />论文</span
      ><span><i style="background: #6a5ac4" />方法 / 数据 / 指标</span
      ><span><i style="background: #c97b5a" />主张</span
      ><span>拖动节点 · 滚轮缩放 · 点击查看依据</span>
    </div>
    <div class="map-layout">
      <div ref="canvas" class="canvas" aria-label="研究关系图" />
      <aside v-if="selected">
        <button
          class="detail-close"
          aria-label="关闭图谱详情"
          @click="selected = null"
        >
          关闭 ×
        </button>
        <p class="library-kicker">SOURCE DETAIL</p>
        <h3>{{ 'name' in selected ? selected.name : selected.type }}</h3>
        <p>{{ 'name' in selected ? selected.type : '关系' }}</p>
        <p>
          来源：{{
            selected.source_status === 'available'
              ? `第 ${selected.citation.page} 页`
              : '来源已删除'
          }}
        </p>
        <p>
          核验：{{
            selected.confidence === 'source_matched' ? '原文匹配' : '待核验'
          }}
        </p>
        <button
          v-if="selected.source_status === 'available'"
          @click="openSource"
        >
          查看原文 →
        </button>
      </aside>
    </div>
    <p v-if="!building && !graph?.nodes.length" class="rs-empty">
      暂无图谱。添加并索引论文后点击“构建研究图谱”。
    </p>
  </section>
</template>
<style scoped>
.rs-feature-page {
  min-width: 0;
  overflow-wrap: anywhere;
}
.heading {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 15px;
}
.heading button {
  border: 0;
  border-radius: 8px;
  background: #5546b7;
  color: white;
  padding: 10px 16px;
  cursor: pointer;
}
.heading button:disabled {
  opacity: 0.6;
}
.toolbar {
  display: flex;
  gap: 20px;
  align-items: center;
  color: #69788e;
  margin: 20px 0;
}
.toolbar select {
  padding: 6px;
  border: 1px solid #d8e0eb;
  border-radius: 7px;
}
.map-layout {
  display: flex;
  gap: 14px;
}
.canvas {
  width: 100%;
  height: 560px;
  background: white;
  border: 1px solid #e1e7f0;
  border-radius: 13px;
}
.map-layout aside {
  width: 250px;
  flex: none;
  background: white;
  border: 1px solid #e1e7f0;
  border-radius: 13px;
  padding: 18px;
  overflow-wrap: anywhere;
}
.map-layout aside button {
  border: 0;
  background: none;
  color: #5546b7;
  cursor: pointer;
}
.error {
  color: #b24e5b;
}
@media (max-width: 900px) {
  .map-layout {
    flex-direction: column;
  }
  .map-layout aside {
    width: auto;
  }
}
.canvas {
  background-color: white;
  background-image: radial-gradient(#dedce6 0.8px, transparent 0.8px);
  background-size: 22px 22px;
  border-color: var(--rs-line);
  border-radius: 14px;
}
.map-layout aside {
  border-color: var(--rs-line);
  border-radius: 14px;
}
.detail-close {
  display: block;
  margin-left: auto;
  font-size: 11px;
}
.map-layout {
  align-items: flex-start;
}
.map-layout aside {
  position: sticky;
  top: 20px;
}
.toolbar {
  flex-wrap: wrap;
  font-size: 12px;
}
.map-controls {
  display: flex;
  gap: 6px;
  margin-left: auto;
}
.map-controls button {
  border: 1px solid var(--rs-line);
  padding: 7px 12px;
  background: white;
  border-radius: 8px;
}
.map-legend {
  font-size: 11px;
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  color: var(--rs-muted);
  margin-bottom: 14px;
}
.map-legend span {
  display: flex;
  align-items: center;
  gap: 6px;
}
.map-legend i {
  width: 7px;
  height: 7px;
  border-radius: 50%;
}
.map-layout aside p {
  font-size: 13px;
  line-height: 1.8;
}
.map-layout aside h3 {
  font-size: 20px;
  line-height: 1.5;
}
@media (max-width: 600px) {
  .canvas {
    height: 420px;
  }
  .map-controls {
    margin-left: 0;
  }
  .map-layout aside {
    position: static;
  }
}
</style>
