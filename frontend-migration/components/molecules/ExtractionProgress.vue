<template>
  <div
    class="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-gray-900/70 backdrop-blur-sm"
    role="status"
    aria-live="polite"
    aria-label="Extraction in progress"
  >
    <div class="mx-4 w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">

      <!-- Header -->
      <div class="mb-5 flex items-center gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-100"
          aria-hidden="true"
        >
          <svg
            class="h-5 w-5 text-primary-600"
            :class="hasActiveStep ? 'animate-spin' : ''"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
        </div>
        <div class="min-w-0">
          <h3 class="text-lg font-semibold text-secondary-800">
            Extracting metadata
          </h3>
          <p class="truncate text-sm text-gray-500">
            {{ activeStep ? activeStep.label : 'Please wait…' }}
          </p>
        </div>
      </div>

      <!-- Dynamic step list -->
      <div class="rounded-xl border border-gray-100 bg-gray-50/50 py-1">
        <!-- Empty state: no events received yet -->
        <div
          v-if="steps.length === 0"
          class="flex items-center gap-2 px-4 py-3 text-sm text-gray-400"
        >
          <svg class="h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          Starting…
        </div>

        <!-- Scrollable step list -->
        <div
          v-else
          ref="scrollContainer"
          class="max-h-60 overflow-y-auto px-1 py-0.5 scroll-smooth"
        >
          <ul class="space-y-0.5 text-sm" aria-hidden="true">
            <li
              v-for="(step, index) in steps"
              :key="step.step"
              class="flex items-start gap-3 rounded-lg px-3 py-2 transition-colors duration-200"
              :class="{
                'bg-primary-50': step.status === 'started',
                'text-gray-700': step.status === 'completed',
              }"
            > <p>{{ index + 1 }} / {{ UIPipelineSize }}</p>
              <!-- Step status icon -->
              <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center">
                <!-- Completed -->
                <span
                  v-if="step.status === 'completed'"
                  class="flex h-6 w-6 items-center justify-center rounded-full bg-green-100 text-green-600"
                >
                  <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                  </svg>
                </span>
                <!-- Active / started -->
                <span
                  v-else-if="step.status === 'started'"
                  class="flex h-6 w-6 items-center justify-center rounded-full bg-primary-200"
                >
                  <svg class="h-3.5 w-3.5 animate-spin text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                </span>
                <!-- Pending -->
                <span
                  v-else
                  class="flex h-6 w-6 items-center justify-center rounded-full border border-gray-200 bg-white text-xs font-medium text-gray-400"
                >
                  {{ index + 1 }}
                </span>
              </span>

              <!-- Label -->
              <div class="min-w-0 flex-1 pt-0.5">
                <span
                  class="font-medium"
                  :class="{
                    'text-primary-700': step.status === 'started',
                    'text-gray-700': step.status === 'completed',
                  }"
                >
                  {{ step.label }}
                </span>
              </div>
            </li>
          </ul>
        </div>

      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExtractionProgress as Progress } from '../../composables/useApi'

const props = defineProps<{
  progressQueue: Progress[] | null
}>()

const stepMap = ref<Map<string, Progress>>(new Map())
const scrollContainer = ref<HTMLElement | null>(null)
const pipelineSize = ref<number | null>(null)

onMounted(() => {
  stepMap.value = new Map()
})

onUnmounted(() => {
  stepMap.value.clear()
})

const UIPipelineSize = computed(() => {
  if (pipelineSize.value !== null) return pipelineSize.value
  return stepMap.value.size > 0 ? stepMap.value.size : null
})

watch(
  () => props.progressQueue,
  (queue) => {
    if (!queue || !queue.length) return
    for (const p of queue) {
      stepMap.value.set(p.step, p)
      if (p.pipeline_size) {
        pipelineSize.value = p.pipeline_size
      }
    }

    stepMap.value = new Map(stepMap.value)

    // After the DOM updates, scroll the container to the bottom so the
    // latest step is always visible without forcing the user to scroll.
    nextTick(() => {
      if (scrollContainer.value) {
        scrollContainer.value.scrollTop = scrollContainer.value.scrollHeight
      }
    })
  },
  { deep: true }
)

const steps = computed<Progress[]>(() => Array.from(stepMap.value.values()))

const activeStep = computed(() => steps.value.find((s) => s.status === 'started') ?? null)
const hasActiveStep = computed(() => activeStep.value !== null)
</script>
