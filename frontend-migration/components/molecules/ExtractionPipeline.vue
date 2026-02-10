<template>
  <section class="rounded-xl border border-gray-200 bg-white shadow-sm p-4 sm:p-8 md:p-10 min-w-0 overflow-hidden">
    <h2 class="text-xl sm:text-2xl font-bold text-secondary-800 mb-4 sm:mb-8 text-center md:text-left">
      Extraction pipeline
    </h2>

    <!-- Mobile: vertical list (no horizontal overflow) -->
    <div class="md:hidden flex flex-col gap-0">
      <template v-for="(step, index) in pipelineSteps" :key="step.id">
        <div class="flex items-center gap-3">
          <div class="flex flex-col items-center flex-shrink-0">
            <div
              class="w-11 h-11 rounded-full border-2 flex items-center justify-center pipeline-dot overflow-hidden"
              :class="step.disabled ? 'border-gray-300 bg-gray-50' : 'border-primary-400 bg-primary-50 pipeline-dot-active'"
            >
              <component :is="step.icon" class="w-5 h-5 flex-shrink-0" :class="step.disabled ? 'text-gray-400' : 'text-primary-600'" />
            </div>
            <div
              v-if="index < pipelineSteps.length - 1"
              class="w-0.5 mt-1 mb-0.5 min-h-[12px] bg-primary-300 pipeline-connector-vertical rounded-full"
            />
          </div>
          <span
            class="text-sm font-medium pt-1 flex-1 min-w-0"
            :class="[step.disabled ? 'text-gray-400 opacity-50' : 'text-secondary-700']"
          >
            {{ step.label }}
          </span>
        </div>
      </template>
    </div>

    <!-- Desktop: horizontal layout with gaps (from md up) -->
    <div class="hidden md:block">
      <div class="flex flex-wrap items-center justify-center gap-3 lg:gap-4 min-w-0">
        <template v-for="(step, index) in pipelineSteps" :key="step.id">
          <div
            v-if="index > 0"
            class="flex-shrink-0 w-12 lg:w-20 h-1.5 lg:h-2 rounded-full self-center pipeline-line bg-primary-300 pipeline-connector"
          />
          <div
            class="flex flex-col items-center flex-shrink-0 pipeline-stage"
            :class="{ 'opacity-50': step.disabled }"
          >
            <div
              class="w-16 lg:w-20 h-16 lg:h-20 rounded-full border-2 flex items-center justify-center flex-shrink-0 pipeline-dot overflow-hidden"
              :class="step.disabled ? 'border-gray-300 bg-gray-50' : 'border-primary-400 bg-primary-50 pipeline-dot-active'"
            >
              <component :is="step.icon" class="w-7 h-7 lg:w-9 lg:h-9 flex-shrink-0" :class="step.disabled ? 'text-gray-400' : 'text-primary-600'" />
            </div>
          </div>
        </template>
      </div>
      <div class="flex flex-wrap items-start justify-center gap-3 lg:gap-4 min-w-0 mt-4">
        <template v-for="(step, index) in pipelineSteps" :key="`label-${step.id}`">
          <div v-if="index > 0" class="flex-shrink-0 w-12 lg:w-20" aria-hidden />
          <div class="flex flex-col items-center justify-start flex-shrink-0 w-16 lg:w-20" :class="{ 'opacity-50': step.disabled }">
            <span
              class="text-sm lg:text-base font-medium text-center leading-tight"
              :class="step.disabled ? 'text-gray-400' : 'text-secondary-700'"
            >
              {{ step.label }}
            </span>
          </div>
        </template>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { h } from 'vue'

// Inline SVG icons (Heroicons-style)
const IconLink = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', 'stroke-width': '1.5', stroke: 'currentColor' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M13.19 8.688a4.5 4.5 0 011.242 7.244l-4.5 4.5a4.5 4.5 0 01-6.364-6.364l1.757-1.757m13.35-.622l1.757-1.757a4.5 4.5 0 00-6.364-6.364l-4.5 4.5a4.5 4.5 0 001.242 7.244' })
  ])
}
const IconCloud = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', 'stroke-width': '1.5', stroke: 'currentColor' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M2.25 15a4.5 4.5 0 004.5 4.5H18a3.75 3.75 0 001.332-7.257 3 3 0 00-3.758-3.848 5.25 5.25 0 00-10.233 2.33A4.502 4.502 0 002.25 15z' })
  ])
}
const IconFolder = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', 'stroke-width': '1.5', stroke: 'currentColor' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M2.25 12.75V12a2.25 2.25 0 012.25-2.25h15a2.25 2.25 0 012.25 2.25v.75m-19.5 0h19.5m-19.5 0V19.5a2.25 2.25 0 002.25 2.25h15a2.25 2.25 0 002.25-2.25V12.75m-19.5 0V6a2.25 2.25 0 012.25-2.25h15a2.25 2.25 0 012.25 2.25v6.75m-19.5 0h19.5' })
  ])
}
const IconGlobe = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', 'stroke-width': '1.5', stroke: 'currentColor' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M12 21a9.004 9.004 0 008.716-6.747M12 21a9.004 9.004 0 01-8.716-6.747M12 21c2.485 0 4.5-4.03 4.5-9S14.485 3 12 3m0 18c-2.485 0-4.5-4.03-4.5-9S9.515 3 12 3m0 0a8.997 8.997 0 017.843 4.582M12 3a8.997 8.997 0 00-7.843 4.582m15.686 0A11.953 11.953 0 0112 10.5c-2.998 0-5.74-1.1-7.843-2.918m15.686 0A8.959 8.959 0 0121 12c0 .778-.099 1.533-.284 2.253m0 0A17.919 17.919 0 0112 16.5c-3.162 0-6.133-.815-8.716-2.247m0 0A9.015 9.015 0 013 12c0-1.605.42-3.113 1.157-4.418' })
  ])
}
const IconSparkles = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', 'stroke-width': '1.5', stroke: 'currentColor' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 00-2.456 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z' })
  ])
}
const IconCode = {
  render: () => h('svg', { xmlns: 'http://www.w3.org/2000/svg', fill: 'none', viewBox: '0 0 24 24', 'stroke-width': '1.5', stroke: 'currentColor' }, [
    h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', d: 'M17.25 6.75L22.5 12l-5.25 5.25m-10.5 0L1.5 12l5.25-5.25m7.5-3l-4.5 16.5' })
  ])
}

const pipelineSteps = [
  { id: 'url', label: 'Get URL', disabled: false, icon: IconLink },
  { id: 'platform', label: 'Platform Extraction', disabled: false, icon: IconCloud },
  { id: 'file_parsing', label: 'File Parsing', disabled: false, icon: IconFolder },
  { id: 'external_data', label: 'External Data', disabled: false, icon: IconGlobe },
  { id: 'llm', label: 'LLM (planned)', disabled: true, icon: IconSparkles },
  { id: 'jsonld', label: 'JSON-LD', disabled: false, icon: IconCode },
]
</script>

<style scoped>
.pipeline-connector {
  background: linear-gradient(90deg, var(--color-primary-300), var(--color-primary-400));
  animation: connector-pulse 2.5s ease-in-out infinite;
}
.pipeline-dot {
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.pipeline-dot-active {
  animation: dot-glow 2.5s ease-in-out infinite;
}
.pipeline-stage:not(.opacity-50):hover .pipeline-dot {
  transform: scale(1.05);
}
@keyframes dot-glow {
  0%, 100% { box-shadow: 0 0 0 0 rgba(147, 51, 234, 0.2); }
  50% { box-shadow: 0 0 0 8px rgba(147, 51, 234, 0); }
}
@keyframes connector-pulse {
  0%, 100% { opacity: 0.9; }
  50% { opacity: 1; }
}
</style>
