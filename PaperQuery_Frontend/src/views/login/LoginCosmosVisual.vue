<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref } from 'vue'
const props = defineProps<{ paused: boolean }>()
const hidden = ref(false)
const reduced = ref(false)
const stopped = computed(() => props.paused || hidden.value || reduced.value)
let media: MediaQueryList | undefined
const syncVisibility = () => { hidden.value = document.hidden }
const syncMotion = () => { reduced.value = media?.matches ?? false }
onMounted(() => {
  media = window.matchMedia('(prefers-reduced-motion: reduce)')
  syncMotion(); syncVisibility()
  media.addEventListener('change', syncMotion)
  document.addEventListener('visibilitychange', syncVisibility)
})
onBeforeUnmount(() => {
  media?.removeEventListener('change', syncMotion)
  document.removeEventListener('visibilitychange', syncVisibility)
})
</script>
<template>
  <div class="login-cosmos" :class="{ 'is-stopped': stopped }" aria-hidden="true">
    <div class="cosmos-image" />
    <div class="cosmos-vignette" />
    <div class="cosmos-orbit"><i /></div>
  </div>
</template>
<style scoped>
.login-cosmos { position:absolute; inset:0; overflow:hidden; pointer-events:none; background:#080d18; }
.cosmos-image { position:absolute; inset:0; background:url('/visuals/research-eclipse.png') center 30% / cover no-repeat; opacity:.85; animation:cosmos-breathe 28s ease-in-out infinite alternate; }
.cosmos-vignette { position:absolute; inset:0; background:linear-gradient(90deg,rgba(8,13,24,.12),transparent 35%,rgba(8,13,24,.45) 70%,#080d18),linear-gradient(0deg,#080d18 0%,rgba(8,13,24,.8) 15%,transparent 80%); }
.cosmos-orbit { position:absolute; left:18%; top:15%; width:44vw; height:44vw; border:1px solid rgba(237,211,170,.13); border-radius:50%; transform:rotate(-20deg); animation:orbit-turn 80s linear infinite; }
.cosmos-orbit i { position:absolute; width:5px; height:5px; left:50%; top:-3px; border-radius:50%; background:#dec39b; box-shadow:0 0 16px #dec39b; }
.is-stopped * { animation-play-state:paused; }
@keyframes cosmos-breathe { to { transform:scale(1.035); } }
@keyframes orbit-turn { to { transform:rotate(340deg); } }
@media(max-width:820px) { .cosmos-image { background-position:35% top; background-size:auto 720px; opacity:.66; } .cosmos-orbit { width:85vw; height:85vw; left:0; top:6%; } }
@media(prefers-reduced-motion:reduce) { .cosmos-image,.cosmos-orbit { animation:none; } }
</style>
