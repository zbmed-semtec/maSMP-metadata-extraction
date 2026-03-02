<template>
  <div class="fair-card">
    <div class="donut-wrapper" role="img" :aria-label="`${indicator.title}: ${percentage}%`">
      <svg viewBox="0 0 36 36" class="donut">
        <circle class="donut-ring" cx="18" cy="18" r="15.9155" fill="transparent" />
        <circle
          class="donut-segment"
          cx="18"
          cy="18"
          r="15.9155"
          fill="transparent"
          :stroke-dasharray="`${percentage} ${100 - percentage}`"
          stroke-dashoffset="25"
        />
        <text x="18" y="20.5" text-anchor="middle" class="donut-label">
          {{ percentage }}%
        </text>
      </svg>
    </div>
    <p class="title">
      {{ indicator.title }}
    </p>
    <p class="meta">
      Principle: {{ principleLabel }}
    </p>
    <p class="status" :class="indicator.score > 0 ? 'status-ok' : 'status-missing'">
      {{ indicator.score > 0 ? 'Satisfied' : 'Not yet satisfied' }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
interface Indicator {
  id: string
  title: string
  principle: string
  score: number
}

const props = defineProps<{
  indicator: Indicator
}>()

const percentage = computed(() => Math.round(Math.max(0, Math.min(1, props.indicator.score)) * 100))

const principleLabel = computed(() => {
  const multiPrinciples: Record<string, string> = {
    bp5_usage_documentation: 'I, R',
    bp8_software_metadata: 'F, R',
  }
  return multiPrinciples[props.indicator.id] ?? props.indicator.principle
})
</script>

<style scoped>
.fair-card {
  @apply rounded-lg border border-gray-200 bg-white px-4 py-3 flex flex-col items-center gap-1;
}

.donut-wrapper {
  width: 80px;
  height: 80px;
  margin-bottom: 4px;
}

.donut {
  width: 100%;
  height: 100%;
}

.donut-ring {
  stroke: #e5e7eb;
  stroke-width: 3;
}

.donut-segment {
  stroke: #7c3aed;
  stroke-width: 3;
  stroke-linecap: round;
  transform: rotate(-90deg);
  transform-origin: center;
}

.donut-label {
  font-size: 8px;
  fill: #111827;
}

.title {
  @apply text-xs font-semibold text-gray-700 text-center;
}

.meta {
  @apply text-[11px] uppercase tracking-wide text-gray-500;
}

.status {
  @apply text-xs font-semibold;
}

.status-ok {
  @apply text-green-600;
}

.status-missing {
  @apply text-red-600;
}
</style>

