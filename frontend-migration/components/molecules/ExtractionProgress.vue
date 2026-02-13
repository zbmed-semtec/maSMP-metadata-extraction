<template>
  <div
    class="fixed inset-0 z-[100] flex flex-col items-center justify-center bg-gray-900/70 backdrop-blur-sm"
    role="status"
    aria-live="polite"
    aria-label="Extraction in progress"
  >
    <div class="mx-4 w-full max-w-md rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
      <div class="mb-5 flex items-center gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-100"
          aria-hidden="true"
        >
          <svg
            class="h-5 w-5 animate-spin text-primary-600"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <circle
              class="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              stroke-width="4"
            />
            <path
              class="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
        <div class="min-w-0">
          <h3 class="text-lg font-semibold text-secondary-800">
            Extracting metadata
          </h3>
          <p class="text-sm text-gray-500">
            Please wait while we analyze the repository.
          </p>
        </div>
      </div>

      <!-- Single progress list: no duplicate "current stage" box -->
      <div class="rounded-xl border border-gray-100 bg-gray-50/50 py-1">
        <ul class="space-y-0.5 px-1 py-0.5 text-sm" aria-hidden="true">
          <li
            v-for="step in steps"
            :key="step.id"
            class="flex items-start gap-3 rounded-lg px-3 py-2 transition-colors"
            :class="
              step.active
                ? 'bg-primary-50 text-primary-800'
                : step.completed
                  ? 'text-gray-600'
                  : 'text-gray-400'
            "
          >
            <span class="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center">
              <span
                v-if="step.completed"
                class="flex h-6 w-6 items-center justify-center rounded-full bg-green-100 text-green-600"
              >
                <svg class="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </span>
              <span
                v-else-if="step.active"
                class="flex h-6 w-6 items-center justify-center rounded-full bg-primary-200"
              >
                <svg class="h-3.5 w-3.5 animate-spin text-primary-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
              </span>
              <span
                v-else
                class="flex h-6 w-6 items-center justify-center rounded-full border border-gray-200 bg-white text-gray-400 text-xs font-medium"
              >
                {{ step.order }}
              </span>
            </span>
            <div class="min-w-0 flex-1 pt-0.5">
              <span
                class="font-medium"
                :class="step.active ? 'text-primary-700' : step.completed ? 'text-gray-700' : 'text-gray-500'"
              >
                {{ step.label }}
              </span>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { ExtractionProgress as Progress } from '../../composables/useApi'

const STEP_ORDER = ['platform', 'file_parsing', 'external_data', 'llm', 'jsonld_build']

const props = defineProps<{
  currentStep: Progress | null
}>()

const currentStepId = computed(() => props.currentStep?.step ?? null)
const currentLabel = computed(() => props.currentStep?.label ?? null)

const completedSteps = ref<Set<string>>(new Set())

watch(
  () => props.currentStep,
  (p) => {
    if (!p) return
    if (p.step === 'platform' && p.status === 'started') completedSteps.value = new Set()
    if (p.status === 'completed') completedSteps.value.add(p.step)
  },
  { immediate: true }
)

const steps = computed(() =>
  STEP_ORDER.map((id, index) => {
    const isCompleted = completedSteps.value.has(id)
    const isActive = props.currentStep?.step === id && props.currentStep?.status === 'started'
    return {
      id,
      order: index + 1,
      label: props.currentStep?.step === id ? props.currentStep?.label : stepLabel(id),
      completed: isCompleted,
      active: isActive
    }
  })
)

function stepLabel(stepId: string): string {
  const labels: Record<string, string> = {
    platform: 'Extracting from platform API (GitHub/GitLab)',
    file_parsing: 'Parsing repository files',
    external_data: 'Fetching external data (OpenAlex, Wayback)',
    llm: 'Extracting with LLM',
    jsonld_build: 'Building JSON-LD document'
  }
  return labels[stepId] ?? stepId
}
</script>
