import { onBeforeUnmount, onMounted, watch, type Ref } from 'vue'
import { recordReading } from '@/api/dashboard'

/** Count only loaded, focused, visible reading intervals; keep document ownership across route reuse. */
export function useReadingTracker(knowledgeID: Ref<string>, documentID: Ref<string>, ready: Ref<boolean>) {
  let currentKnowledge = knowledgeID.value
  let currentDocument = documentID.value
  let lastTick = Date.now()
  let pendingMs = 0
  let active = false
  let mounted = false
  let timer: ReturnType<typeof setInterval> | undefined
  const accrue = () => {
    const now = Date.now()
    if (active) pendingMs += Math.max(0, Math.min(30000, now - lastTick))
    lastTick = now
  }
  const flush = () => {
    accrue()
    const seconds = Math.floor(pendingMs / 1000)
    pendingMs -= seconds * 1000
    if (seconds > 0 && currentKnowledge && currentDocument) {
      recordReading(currentKnowledge, currentDocument, seconds).catch(error => console.error('阅读时长记录失败', error))
    }
  }
  const reconcile = () => {
    accrue()
    active = mounted && ready.value && document.visibilityState === 'visible' && document.hasFocus()
  }
  const pause = () => { accrue(); active = false; flush() }
  watch(ready, reconcile, { flush: 'sync' })
  watch([knowledgeID, documentID], ([knowledge, doc]) => {
    flush()
    active = false
    pendingMs = 0
    currentKnowledge = knowledge
    currentDocument = doc
    // The page resets its loaded state; ready may be a readonly computed gate.
    lastTick = Date.now()
  }, { flush: 'sync' })
  onMounted(() => {
    mounted = true
    reconcile()
    timer = setInterval(flush, 15000)
    window.addEventListener('focus', reconcile)
    window.addEventListener('blur', pause)
    window.addEventListener('pagehide', pause)
    document.addEventListener('visibilitychange', reconcile)
  })
  onBeforeUnmount(() => {
    flush()
    mounted = false
    active = false
    clearInterval(timer)
    window.removeEventListener('focus', reconcile)
    window.removeEventListener('blur', pause)
    window.removeEventListener('pagehide', pause)
    document.removeEventListener('visibilitychange', reconcile)
  })
}
