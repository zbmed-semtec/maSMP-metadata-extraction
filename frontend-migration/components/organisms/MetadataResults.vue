<template>
  <div class="space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-4">
      <h2 class="text-xl font-semibold text-secondary-800">
        Extraction results
      </h2>
      <Button
        type="button"
        variant="secondary"
        size="small"
        custom-class="inline-flex items-center gap-2"
        @click="downloadJsonLd"
      >
        <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        Download JSON-LD
      </Button>
    </div>

    <!-- maSMP: tabs + Required / Recommended / Optional -->
    <template v-if="isMaSMP">
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex gap-4" aria-label="Result profiles">
          <button
            v-for="tab in masmpTabs"
            :key="tab.key"
            type="button"
            :class="[
              'border-b-2 px-1 py-3 text-sm font-medium transition-colors',
              activeTab === tab.key
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
            ]"
            @click="activeTab = tab.key"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>
      <div v-for="category in categories" :key="category" class="space-y-3">
        <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-600">
          {{ category }}
        </h3>
        <ResultTable
          :rows="rowsByCategory(activeTab, category)"
          :show-source="true"
          :show-confidence="true"
        />
      </div>
    </template>

    <!-- CodeMeta: single section -->
    <template v-else>
      <h3 class="text-sm font-semibold uppercase tracking-wide text-gray-600">
        CodeMeta metadata
      </h3>
      <ResultTable
        :rows="codemetaRows"
        :show-source="false"
        :show-confidence="false"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import type { ExtractionStreamResult, EnrichedProperty } from '../../composables/useApi'

const props = defineProps<{
  result: ExtractionStreamResult
}>()

const categories = ['Required', 'Recommended', 'Optional'] as const
const masmpTabs = [
  { key: 'maSMP:SoftwareSourceCode', label: 'Software source code' },
  { key: 'maSMP:SoftwareApplication', label: 'Software application' }
]

const activeTab = ref('maSMP:SoftwareSourceCode')

const isMaSMP = computed(() => {
  const s = props.result.schema?.toLowerCase()
  return s === 'masmp' || s === 'maSMP'
})

const profileData = (profileKey: string): Record<string, unknown> => {
  const data = props.result.results?.[profileKey]
  return data && typeof data === 'object' && !Array.isArray(data) ? data as Record<string, unknown> : {}
}

const enrichedForProfile = (profileKey: string): Record<string, EnrichedProperty> => {
  const data = props.result.enriched_metadata?.[profileKey]
  return data && typeof data === 'object' ? data as Record<string, EnrichedProperty> : {}
}

function rowsByCategory(profileKey: string, category: string): { property: string; value: string; source: string; confidence: string }[] {
  const data = profileData(profileKey)
  const enriched = enrichedForProfile(profileKey)
  const skip = new Set(['@context', '@type'])
  const catLower = category.toLowerCase()
  return Object.entries(data)
    .filter(([k]) => !skip.has(k))
    .filter(([k]) => {
      const c = enriched[k]?.category ?? 'optional'
      return (typeof c === 'string' ? c.toLowerCase() : 'optional') === catLower
    })
    .map(([prop, val]) => {
      const meta = enriched[prop]
      return {
        property: formatPropertyName(prop),
        value: formatValue(val),
        source: meta?.source ?? '—',
        confidence: meta?.confidence != null ? `${Math.round(Number(meta.confidence) * 100)}%` : '—'
      }
    })
}

const codemetaRows = computed(() => {
  const data = props.result.results
  if (!data || typeof data !== 'object' || Array.isArray(data)) return []
  const skip = new Set(['@context', '@type'])
  return Object.entries(data)
    .filter(([k]) => !skip.has(k))
    .map(([prop, val]) => ({
      property: formatPropertyName(prop),
      value: formatValue(val),
      source: '—',
      confidence: '—'
    }))
})

function formatPropertyName(key: string): string {
  return key.replace(/^[^:]+:/, '').replace(/([A-Z])/g, ' $1').trim() || key
}

function formatValue(val: unknown): string {
  if (val == null) return '—'
  if (typeof val === 'string') return val
  if (typeof val === 'number' || typeof val === 'boolean') return String(val)
  if (Array.isArray(val)) return val.map(v => formatValue(v)).join(', ')
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

function downloadJsonLd() {
  const blob = new Blob([JSON.stringify(props.result.results, null, 2)], { type: 'application/ld+json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `metadata-${props.result.schema ?? 'export'}-${Date.now()}.jsonld`
  a.click()
  URL.revokeObjectURL(url)
}
</script>
