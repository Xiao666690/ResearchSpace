<script setup lang="ts">
defineProps<{ eyebrow: string; title: string; description?: string }>()
</script>
<template>
  <header class="rs-feature-heading">
    <div>
      <p class="rs-kicker">{{ eyebrow }}</p>
      <h2>{{ title }}</h2>
      <p v-if="description" class="rs-description">{{ description }}</p>
    </div>
    <div class="rs-heading-actions"><slot /></div>
  </header>
</template>
<style scoped>
.rs-feature-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin: 0 0 24px;
}
.rs-kicker {
  font-size: 10px;
  letter-spacing: 0.18em;
  font-weight: 650;
  color: var(--rs-primary, #6858d6);
  margin: 0 0 8px;
}
.rs-feature-heading h2 {
  font-size: clamp(24px, 2.3vw, 32px);
  letter-spacing: -0.04em;
  font-weight: 600;
  line-height: 1.3;
  margin: 0;
  color: var(--rs-ink, #202124);
}
.rs-description {
  max-width: 660px;
  line-height: 1.7;
  color: var(--rs-muted, #687078);
  font-size: 14px;
  margin: 10px 0 0;
}
.rs-heading-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  flex-shrink: 0;
}
@media (max-width: 600px) {
  .rs-feature-heading {
    flex-direction: column;
    gap: 14px;
  }
}
</style>
