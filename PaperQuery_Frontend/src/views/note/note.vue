<template>
  <div class="note-panel" :class="{ 'load-failed': loadError }">
    <div class="note-status" role="status"><span class="note-label">RESEARCH NOTES</span><span :class="{ 'status-error': loadError || status.includes('失败') }">{{ status }}</span><button v-if="loadError" type="button" @click="loadInitialNote">重新加载</button></div>
    <div class="note-actions">
      <div class="actions-left">
        <button type="button" title="将剪贴板中的 Markdown 原文插入光标位置" :disabled="loading || loadError" @click="pasteMarkdown">粘贴 AI Markdown</button>
        <button type="button" title="导入本地 .md 文件并插入光标位置" :disabled="loading || loadError" @click="fileInput?.click()">导入 Markdown</button>
      </div>
      <div class="actions-right">
        <button v-if="!hideFullscreen" type="button" title="进入左论文右笔记的全屏编辑页" @click="goFullscreen">全屏编辑</button>
        <button type="button" :disabled="loading || loadError" @click="exportNote">导出 Markdown</button>
        <button type="button" class="primary" :disabled="saving || loading || loadError" @click="saveNote(true)">{{ saving ? '保存中…' : '保存' }}</button>
      </div>
    </div>
    <input ref="fileInput" type="file" accept=".md,.markdown,text/markdown,text/plain" hidden @change="importMarkdown" />
    <div :id="editorId" class="note-editor" ref="noteEditorRef" :inert="loading || loadError" />
  </div>
</template>

<style scoped>
.note-panel { display: flex; flex-direction: column; height: 100%; min-height: 0; }
/* 笔记操作栏：5 个按钮白底黑字、点击带外阴影按压反馈 */
.note-actions { padding: 10px 12px; display: flex; align-items: center; gap: 8px; flex: none; flex-wrap: wrap; padding: 10px 12px; }
.actions-left, .actions-right { display: flex; align-items: center; gap: 8px; }
.actions-right { margin-left: auto; } /* 主操作靠右，保存放最右 */
.note-actions button {
  height: 30px; padding: 0 14px; font-size: 12px; line-height: 1; white-space: nowrap;
  background: #ffffff;             /* 白底 */
  color: #1f1f1f;                  /* 黑字 */
  border: 1px solid #d0d0d8;       /* 细浅灰描边，白底不显得空 */
  border-radius: 8px; cursor: pointer;
  transition: background .12s ease, color .12s ease, transform .12s ease, box-shadow .12s ease;
}
.note-actions button:hover { background: #f5f5f9; } /* hover 略灰 */
.note-actions button:active { transform: scale(.96); box-shadow: 0 2px 8px rgba(31,31,31,.22); } /* 点击外阴影按压 */
.note-actions button:disabled { opacity: .5; cursor: not-allowed; }
.note-actions .primary { background: var(--rs-primary,#6858D6); color: #fff; }
.note-actions .primary:hover { background: #5a4bbd; }
.note-editor { position: relative; flex: 1; min-height: 0; overflow: auto; }
/* 滚动反馈：可滚动时在编辑区顶部/底部显示渐隐阴影，指示滚动方向 */
.note-editor :deep(.vditor-content) { position: relative; scroll-behavior: auto; }
.note-editor :deep(.vditor-ir) { scroll-behavior: auto; }
.note-editor :deep(.vditor-content)::before,
.note-editor :deep(.vditor-content)::after {
  content: ''; position: absolute; left: 0; right: 0; height: 24px; pointer-events: none;
  opacity: 0; transition: opacity .15s ease; z-index: 5;
}
.note-editor :deep(.vditor-content)::before { top: 0; background: linear-gradient(180deg, rgba(30, 30, 60, .08), transparent); }
.note-editor :deep(.vditor-content)::after { bottom: 0; background: linear-gradient(0deg, rgba(30, 30, 60, .08), transparent); }
.note-editor :deep(.vditor-content.show-top)::before { opacity: 1; }
.note-editor :deep(.vditor-content.show-bottom)::after { opacity: 1; }
/* Vditor 透明融入纸面：编辑器背景透明、工具栏半透明米白、隐藏右下角拖拽把手 */
.note-editor :deep(.vditor) { background: transparent; }
.note-editor :deep(.vditor-content) { background: transparent; }
.note-editor :deep(.vditor-toolbar) { flex-wrap: wrap; gap: 2px; background: rgba(251,250,246,.92); border-bottom: 1px solid rgba(109,91,208,.12); }
.note-editor :deep(.vditor-toolbar__item:hover) { background: rgba(109,91,208,.12); border-radius: 5px; }
.note-editor :deep(.vditor-resize) { display: none; }
.note-status{display:flex;align-items:center;gap:12px;justify-content:space-between;flex-wrap:wrap;padding:10px 14px;border-bottom:1px solid #E8E5DD;background:#FBFAF7;font-size:10px;color:#687078}.note-label{letter-spacing:.14em;font-size:9px}.status-error{color:#A24836}.note-status button{color:#6858D6;text-decoration:underline}.note-actions .primary{min-width:72px;border-color:transparent}.note-actions button:focus-visible{outline:2px solid #6858D6;outline-offset:2px}.load-failed .note-editor{pointer-events:none;opacity:.5}.note-editor :deep(.vditor-reset){font-size:16px;line-height:1.9;color:#202124}.note-editor :deep(.vditor){border-color:#E5E3DC}.note-editor :deep(.vditor-ir){background:#FFFEFC}@media(max-width:480px){.actions-left,.actions-right{gap:4px}.note-actions button{padding:0 8px}.actions-right{margin-left:0}}@media(prefers-reduced-motion:reduce){.note-actions button{transition:none}.note-actions button:active{transform:none}}
</style>

<script setup lang="ts">
import Vditor from 'vditor'
import 'vditor/dist/index.css'
import { ElMessage } from 'element-plus'
import { useRouter, onBeforeRouteLeave, onBeforeRouteUpdate } from 'vue-router'
import { getDocumentNote, updateDocumentNote } from '@/api/note'

const props = defineProps<{ knowledgeID: string; documentID: string; hideFullscreen?: boolean }>()
const router = useRouter()
const goFullscreen = () => router.push({
  name: 'noteFullscreen',
  params: { knowledgeID: props.knowledgeID, documentID: props.documentID },
})
const editorId = `paper-note-${props.documentID.replace(/[^a-zA-Z0-9_-]/g, '-')}`
const editor = ref<Vditor | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const noteEditorRef = ref<HTMLElement | null>(null)
const status = ref('正在加载笔记…')
const saving = ref(false)
let saveTimer: ReturnType<typeof setTimeout> | undefined
const loading = ref(true)
const loadError = ref(false)
let queuedContent: string | null = null
let lastSavedContent: string | null = null
let disposed = false
let saveJob: Promise<void> | null = null

const saveNote = (notify = false): Promise<void> => {
  if (!editor.value || loading.value || loadError.value) return Promise.resolve()
  queuedContent = editor.value.getValue()
  clearTimeout(saveTimer)
  if (saveJob) return saveJob
  saving.value = true
  const knowledge = props.knowledgeID
  const doc = props.documentID
  saveJob = (async () => {
    while (queuedContent !== null) {
      const content = queuedContent
      queuedContent = null
      if (!disposed) status.value = '保存中…'
      try {
        await updateDocumentNote(knowledge, doc, content)
        lastSavedContent = content
        if (!disposed) {
          status.value = editor.value?.getValue() === content ? `已保存 ${new Date().toLocaleTimeString()}` : '未保存的修改'
          if (notify && queuedContent === null) ElMessage.success('笔记已保存')
        }
      } catch (error: any) {
        if (!disposed) { status.value = '保存失败，请重试'; ElMessage.error(error?.message || '笔记保存失败') }
        else console.error('离开页面后的笔记保存失败', error)
        queuedContent = null
      }
    }
  })().finally(() => { saving.value = false; saveJob = null })
  return saveJob
}

const protectUnsavedNote = async () => {
  if (loading.value || loadError.value || !editor.value) return true
  if (saveJob) await saveJob
  if (editor.value && editor.value.getValue() !== lastSavedContent) await saveNote()
  return !editor.value || editor.value.getValue() === lastSavedContent
}
onBeforeRouteLeave(protectUnsavedNote)
onBeforeRouteUpdate((to, from) => {
  if (to.params.documentID === from.params.documentID && to.params.knowledgeID === from.params.knowledgeID) return true
  return protectUnsavedNote()
})
const onInput = () => {
  if (loading.value || loadError.value) return
  status.value = '未保存的修改'
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => saveNote(), 1000)
}

const exportNote = () => {
  const content = editor.value?.getValue() || ''
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = `ResearchSpace_笔记_${props.documentID}.md`
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 1000)
}

const pasteMarkdown = async () => {
  try {
    const markdown = await navigator.clipboard.readText()
    if (!markdown.trim()) return ElMessage.info('剪贴板中没有文字')
    if (disposed || loading.value || loadError.value) return
    editor.value?.insertMD(markdown)
    onInput()
  } catch { ElMessage.warning('无法读取剪贴板，请在编辑区使用 Ctrl+V 粘贴') }
}

const importMarkdown = async (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) { ElMessage.warning('请选择小于 2 MB 的 Markdown 文件'); input.value = ''; return }
  const markdown = await file.text()
  if (disposed || loading.value || loadError.value) return
  editor.value?.insertMD(markdown)
  input.value = ''
  onInput()
}

// 滚动视觉反馈：可滚动时在编辑区顶部/底部显示渐隐阴影
let scrollTargets: HTMLElement[] = []
const applyScrollHints = (target: HTMLElement) => {
  const contentEl = noteEditorRef.value?.querySelector<HTMLElement>('.vditor-content')
  if (!contentEl) return
  const { scrollTop, clientHeight, scrollHeight } = target
  const canScroll = scrollHeight - clientHeight > 2
  contentEl.classList.toggle('show-top', canScroll && scrollTop > 2)
  contentEl.classList.toggle('show-bottom', canScroll && scrollTop + clientHeight < scrollHeight - 2)
}
const onEditorScroll = (event: Event) => applyScrollHints(event.currentTarget as HTMLElement)

const onKeyDown = (event: KeyboardEvent) => {
  if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 's') {
    event.preventDefault()
    saveNote(true)
  }
}

const loadInitialNote = async () => {
  loading.value = true
  loadError.value = false
  status.value = '正在加载笔记…'
  try {
    const response = await getDocumentNote(props.knowledgeID, props.documentID)
    if (disposed) return
    lastSavedContent = response.data?.note || '# 我的笔记\n'
    editor.value?.setValue(lastSavedContent)
    status.value = '已加载 · 修改后自动保存'
    loading.value = false
  } catch {
    if (disposed) return
    loadError.value = true
    status.value = '无法读取笔记，请重试；已暂停编辑以保护原笔记。'
  }
}
onMounted(() => {
  editor.value = new Vditor(editorId, {
    height: '100%', width: '100%', mode: 'ir',
    lang: 'zh_CN',
    toolbarConfig: { pin: true },
    counter: { enable: true, type: 'markdown' },
    toolbar: [
      { name: 'headings', tip: '标题' }, { name: 'bold', tip: '加粗' }, { name: 'italic', tip: '斜体' },
      { name: 'strike', tip: '删除线' }, '|', { name: 'list', tip: '无序列表' },
      { name: 'ordered-list', tip: '有序列表' }, { name: 'check', tip: '任务列表' },
      { name: 'quote', tip: '引用' }, { name: 'line', tip: '分隔线' }, '|',
      { name: 'code', tip: '代码块' }, { name: 'inline-code', tip: '行内代码' },
      { name: 'link', tip: '链接' }, { name: 'table', tip: '表格' }, '|',
      { name: 'undo', tip: '撤销' }, { name: 'redo', tip: '重做' },
      { name: 'outline', tip: '大纲' }, { name: 'edit-mode', tip: '切换编辑模式' },
    ],
    cache: { enable: false },
    input: onInput,
    after: async () => {
      await loadInitialNote()
      {
        // 挂载滚动事件：用实际滚动容器驱动阴影显隐
        scrollTargets = Array.from(noteEditorRef.value?.querySelectorAll<HTMLElement>('.vditor-content, .vditor-ir') || [])
        scrollTargets.forEach((el) => el.addEventListener('scroll', onEditorScroll, { passive: true }))
        const scroller = scrollTargets.find((el) => el.scrollHeight - el.clientHeight > 2) || scrollTargets[0]
        if (scroller) applyScrollHints(scroller)
      }
    },
  })
  window.addEventListener('keydown', onKeyDown)
})

onBeforeUnmount(() => {
  clearTimeout(saveTimer)
  if (!loading.value && !loadError.value && editor.value && editor.value.getValue() !== lastSavedContent) saveNote()
  disposed = true
  scrollTargets.forEach((el) => el.removeEventListener('scroll', onEditorScroll))
  editor.value?.destroy()
  editor.value = null
  window.removeEventListener('keydown', onKeyDown)
})
</script>
