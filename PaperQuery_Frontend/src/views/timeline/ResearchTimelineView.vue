<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import FeatureHeader from '@/components/research/FeatureHeader.vue'
import { listTimeline, type TimelineEvent } from '@/api/timeline'
const route = useRoute(),
  events = ref<TimelineEvent[]>([]),
  loading = ref(true),
  error = ref(''),
  filter = ref('all')
const labels: Record<string, string> = {
  PROJECT_CREATED: '创建项目',
  PAPER_ADDED: '添加论文',
  PAPER_REMOVED: '移除论文',
  QUESTION_ASKED: '提出问题',
  TASK_CREATED: '创建任务',
  TASK_COMPLETED: '完成任务',
  TASK_FAILED: '任务失败',
  CLAIM_CREATED: '创建观点',
  EVIDENCE_ADDED: '加入证据',
  COMPARISON_CREATED: '完成比较',
  STUDIO_UPDATED: '编辑成果',
  COMMENT_CREATED: '添加评论',
  NOTE_UPDATED: '更新笔记',
}
const kinds = computed(() => [
  ...new Set(events.value.map((item) => item.event_type)),
])
const visibleEvents = computed(() =>
  events.value.filter(
    (item) => filter.value === 'all' || item.event_type === filter.value,
  ),
)
async function load() {
  loading.value = true
  error.value = ''
  try {
    events.value = await listTimeline(String(route.params.projectId))
  } catch {
    error.value = '时间线暂时无法加载，请重试。'
  } finally {
    loading.value = false
  }
}
const date = (value?: string) => {
  if (!value) return '时间未记录'
  const d = new Date(value)
  return Number.isNaN(d.getTime())
    ? '时间未记录'
    : d.toLocaleString('zh-CN', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
}
onMounted(load)
</script>
<template>
  <section class="rs-feature-page">
    <FeatureHeader
      eyebrow="TIME / RESEARCH JOURNEY"
      title="每一步，都在留下轨迹。"
      description="从第一篇论文到最后一份成果，回看研究如何逐渐成形。"
      ><button :disabled="loading" @click="load">
        {{ loading ? '加载中…' : '刷新动态' }}
      </button></FeatureHeader
    >
    <div class="timeline-tools">
      <span>{{ events.length }} 条研究记录</span
      ><label
        >事件类型
        <select v-model="filter">
          <option value="all">全部动态</option>
          <option v-for="kind in kinds" :key="kind" :value="kind">
            {{ labels[kind] || kind }}
          </option>
        </select></label
      >
    </div>
    <p v-if="loading" class="rs-empty" aria-live="polite">正在连接研究轨迹…</p>
    <p v-else-if="error" class="rs-empty">{{ error }}</p>
    <p v-else-if="!visibleEvents.length" class="rs-empty">
      {{
        events.length
          ? '当前类型还没有动态。'
          : '这里将记录你的每一步探索。添加论文或开始研究后，轨迹会出现在这里。'
      }}
    </p>
    <ol v-else class="event-rail">
      <li
        v-for="event in visibleEvents"
        :key="event.id"
        :class="{ failed: event.event_type === 'TASK_FAILED' }"
      >
        <time>{{ date(event.created_at || undefined) }}</time
        ><span class="event-dot" />
        <article>
          <small>{{ labels[event.event_type] || event.event_type }}</small>
          <h3>
            {{ event.title || labels[event.event_type] || event.event_type }}
          </h3>
          <p v-if="event.description && event.description !== event.title">
            {{ event.description }}
          </p>
        </article>
      </li>
    </ol>
  </section>
</template>
<style scoped>
.timeline-tools {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
  padding: 0 0 20px;
  color: var(--rs-muted);
  font-size: 12px;
}
.timeline-tools select {
  border: 1px solid var(--rs-line);
  border-radius: 8px;
  padding: 8px;
  margin-left: 8px;
}
.event-rail {
  list-style: none;
  padding: 8px 0;
  margin: 0;
  max-width: 1000px;
}
.event-rail li {
  display: grid;
  grid-template-columns: 130px 1fr;
  gap: 30px;
  position: relative;
  padding-bottom: 20px;
}
.event-rail li:before {
  position: absolute;
  content: '';
  width: 1px;
  left: 145px;
  top: 8px;
  bottom: -8px;
  background: var(--rs-line);
}
.event-rail li:last-child:before {
  bottom: 30px;
}
.event-dot {
  position: absolute;
  left: 141px;
  top: 13px;
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--rs-primary);
  box-shadow: 0 0 0 5px var(--rs-canvas);
}
time {
  font-size: 11px;
  color: var(--rs-muted);
  padding-top: 12px;
  font-variant-numeric: tabular-nums;
}
article {
  background: white;
  border: 1px solid var(--rs-line);
  border-radius: 12px;
  padding: 20px 24px;
  overflow-wrap: anywhere;
}
article small {
  font-size: 10px;
  color: var(--rs-primary);
}
article h3 {
  font-size: 15px;
  line-height: 1.7;
  font-weight: 550;
  margin: 6px 0 0;
}
article p {
  font-size: 13px;
  color: var(--rs-muted);
  line-height: 1.8;
  margin: 8px 0 0;
}
.failed .event-dot {
  background: #bb5555;
}
.failed article small {
  color: #bb5555;
}
@media (max-width: 600px) {
  .event-rail li {
    grid-template-columns: 1fr;
    gap: 7px;
    padding-left: 22px;
  }
  .event-rail li:before {
    left: 4px;
  }
  .event-dot {
    left: 0;
    top: 17px;
  }
  time {
    padding-top: 8px;
  }
  article {
    padding: 16px;
  }
}
</style>
