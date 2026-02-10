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
      <div class="space-y-8">
        <section
          v-for="cat in categoryConfig"
          :key="cat.key"
          class="rounded-xl border-2 overflow-hidden"
          :class="cat.sectionClass"
        >
          <header
            class="flex items-center gap-3 px-4 py-3 font-semibold"
            :class="cat.headerClass"
          >
            <span
              class="rounded-md px-2.5 py-1 text-xs font-bold uppercase tracking-wider"
              :class="cat.badgeClass"
            >
              {{ cat.key }}
            </span>
            <span :class="cat.titleClass">{{ cat.label }}</span>
          </header>
          <div class="border-t bg-white" :class="cat.borderClass">
            <ResultTable
              :rows="rowsByCategory(activeTab, cat.key)"
              :show-source="true"
              :show-confidence="true"
            />
          </div>
        </section>
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

const categoryConfig = [
  {
    key: 'Required',
    label: 'Must-have properties for this profile',
    sectionClass: 'border-amber-200 bg-amber-50/30',
    headerClass: 'bg-amber-50/80 text-amber-900',
    badgeClass: 'bg-amber-200 text-amber-800',
    titleClass: 'text-amber-900',
    borderClass: 'border-amber-100'
  },
  {
    key: 'Recommended',
    label: 'Recommended for richer metadata',
    sectionClass: 'border-primary-200 bg-primary-50/20',
    headerClass: 'bg-primary-50/80 text-primary-900',
    badgeClass: 'bg-primary-200 text-primary-800',
    titleClass: 'text-primary-900',
    borderClass: 'border-primary-100'
  },
  {
    key: 'Optional',
    label: 'Additional optional properties',
    sectionClass: 'border-slate-200 bg-slate-50/60',
    headerClass: 'bg-slate-100/80 text-slate-700',
    badgeClass: 'bg-slate-200 text-slate-600',
    titleClass: 'text-slate-700',
    borderClass: 'border-slate-100'
  }
] as const

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
