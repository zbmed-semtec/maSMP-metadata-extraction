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

export interface AuthorDisplayItem {
  name: string
  url?: string
}

/** Single name + optional URL (e.g. license, identifier). */
export interface NamedLinkItem {
  name: string
  url?: string
}

/** Reference publication as a bibliography card. */
export interface BibCardItem {
  title: string
  authors: string
  url?: string
}

function rowsByCategory(profileKey: string, category: string): { property: string; value: string; source: string | string[]; confidence: string; authorItems?: AuthorDisplayItem[] }[] {
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
      const authorItems = getAuthorItems(prop, val)
      const contributorItems = getContributorItems(prop, val)
      const namedLink = getNamedLink(prop, val)
      const bibCard = getBibCard(prop, val)
      const useSpecial = authorItems ?? contributorItems ?? namedLink ?? bibCard
      return {
        property: formatPropertyName(prop),
        value: useSpecial ? '' : formatValueForProperty(prop, val),
        source: meta?.source ?? '—',
        confidence: meta?.confidence != null ? `${Math.round(Number(meta.confidence) * 100)}%` : '—',
        ...(authorItems ? { authorItems } : {}),
        ...(contributorItems ? { contributorItems } : {}),
        ...(namedLink ? { namedLink } : {}),
        ...(bibCard ? { bibCard } : {})
      }
    })
}

const codemetaRows = computed(() => {
  const data = props.result.results
  if (!data || typeof data !== 'object' || Array.isArray(data)) return []
  const skip = new Set(['@context', '@type'])
  return Object.entries(data)
    .filter(([k]) => !skip.has(k))
    .map(([prop, val]) => {
      const authorItems = getAuthorItems(prop, val)
      const contributorItems = getContributorItems(prop, val)
      const namedLink = getNamedLink(prop, val)
      const bibCard = getBibCard(prop, val)
      const useSpecial = authorItems ?? contributorItems ?? namedLink ?? bibCard
      return {
        property: formatPropertyName(prop),
        value: useSpecial ? '' : formatValueForProperty(prop, val),
        source: '—',
        confidence: '—',
        ...(authorItems ? { authorItems } : {}),
        ...(contributorItems ? { contributorItems } : {}),
        ...(namedLink ? { namedLink } : {}),
        ...(bibCard ? { bibCard } : {})
      }
    })
})

function formatPropertyName(key: string): string {
  return key.replace(/^[^:]+:/, '').replace(/([A-Z])/g, ' $1').trim() || key
}

/** If property is reference publication (ScholarlyArticle etc.), return bib card data; else null. */
function getBibCard(prop: string, val: unknown): BibCardItem | null {
  const propLower = (formatPropertyName(prop) || prop).toLowerCase().replace(/\s+/g, '')
  const refKeys = ['referencepublication', 'referencePublication', 'codemetareferencepublication']
  if (!refKeys.some(k => propLower.includes(k))) return null
  if (val == null || typeof val !== 'object' || Array.isArray(val)) return null
  const ref = val as Record<string, unknown>
  const title = (ref.name ?? ref.title ?? '') as string
  if (!title || typeof title !== 'string' || !title.trim()) return null
  const authors = formatRefAuthors(ref.author)
  let url: string | undefined
  const rawId = (ref['@id'] ?? ref.id ?? ref.url ?? ref.doi ?? '') as string
  if (rawId && typeof rawId === 'string' && rawId.trim()) {
    url = /^https?:\/\//i.test(rawId) ? rawId : (rawId.startsWith('doi.org') ? `https://${rawId}` : `https://doi.org/${rawId.replace(/^\/+/, '')}`)
  }
  return { title: title.trim(), authors: authors || '—', ...(url ? { url } : {}) }
}

function formatRefAuthors(author: unknown): string {
  if (author == null) return ''
  const list = Array.isArray(author) ? author : [author]
  const names: string[] = []
  for (const item of list) {
    if (item == null || typeof item !== 'object') continue
    const p = item as Record<string, unknown>
    const given = (p.givenName ?? p.given_name ?? '') as string
    const family = (p.familyName ?? p.family_name ?? '') as string
    const name = (p.name as string) ?? [given, family].filter(Boolean).join(' ').trim()
    if (name && typeof name === 'string') names.push(name.trim())
    else if (given || family) names.push([given, family].filter(Boolean).join(' ').trim())
  }
  if (names.length === 0) return ''
  if (names.length === 1) return names[0]
  if (names.length === 2) return `${names[0]} and ${names[1]}`
  return `${names.slice(0, -1).join(', ')}, and ${names[names.length - 1]}`
}

/** If property is license (or similar) with object { name, url? }, return single named link; else null. */
function getNamedLink(prop: string, val: unknown): NamedLinkItem | null {
  const propLower = (formatPropertyName(prop) || prop).toLowerCase()
  if (propLower !== 'license' && propLower !== 'identifier') return null
  if (val == null || typeof val !== 'object' || Array.isArray(val)) return null
  const o = val as Record<string, unknown>
  const name = (o.name ?? o.title ?? '') as string
  if (!name || typeof name !== 'string' || !name.trim()) return null
  let url: string | undefined
  const raw = (o.url ?? o['@id'] ?? o.id ?? '') as string
  if (raw && typeof raw === 'string' && raw.trim()) {
    url = /^https?:\/\//i.test(raw) ? raw : `https://${raw.replace(/^\/+/, '')}`
  }
  return { name: name.trim(), ...(url ? { url } : {}) }
}

/** If property is author, return structured items for pill display; otherwise null. */
function getAuthorItems(prop: string, val: unknown): AuthorDisplayItem[] | null {
  const propLower = (formatPropertyName(prop) || prop).toLowerCase()
  if (propLower !== 'author') return null
  if (val == null) return null
  const list = Array.isArray(val) ? val : (typeof val === 'object' && val !== null ? [val] : null)
  if (!list?.length) return null
  const items: AuthorDisplayItem[] = []
  for (const item of list) {
    const one = toAuthorDisplayItem(item)
    if (one) items.push(one)
  }
  return items.length ? items : null
}

/** If property is contributor, return structured items (name or URL-derived label + link); else null. */
function getContributorItems(prop: string, val: unknown): AuthorDisplayItem[] | null {
  const propLower = (formatPropertyName(prop) || prop).toLowerCase()
  if (propLower !== 'contributor') return null
  if (val == null) return null
  const list = Array.isArray(val) ? val : (typeof val === 'object' && val !== null ? [val] : null)
  if (!list?.length) return null
  const items: AuthorDisplayItem[] = []
  for (const item of list) {
    const one = toContributorDisplayItem(item)
    if (one) items.push(one)
  }
  return items.length ? items : null
}

/** Build a short label from a URL for display (e.g. "dgarijo" from github.com/dgarijo). */
function labelFromUrl(url: string): string {
  try {
    const u = new URL(url)
    const path = u.pathname.replace(/^\/+/, '').split('/').filter(Boolean)
    if (path.length === 0) return u.hostname
    if (path.length === 1) return path[0]
    if (path[0] === 'apps') return path[1] ?? path[0]
    return path[path.length - 1]
  } catch {
    return url.length > 40 ? url.slice(0, 37) + '…' : url
  }
}

/** One contributor: name (or URL label) + optional url. Supports Person with only url (e.g. GitHub). */
function toContributorDisplayItem(person: unknown): AuthorDisplayItem | null {
  if (person == null || typeof person !== 'object') return null
  const p = person as Record<string, unknown>
  const withName = toAuthorDisplayItem(person)
  if (withName) return withName
  const rawUrl = (p.url ?? p['@id'] ?? p.id ?? '') as string
  if (!rawUrl || typeof rawUrl !== 'string' || !rawUrl.trim()) return null
  const url = /^https?:\/\//i.test(rawUrl) ? rawUrl : `https://${rawUrl.replace(/^\/+/, '')}`
  const name = labelFromUrl(url)
  return { name, url }
}

/** Format value for display; use author-specific formatting when property is author (fallback only). */
function formatValueForProperty(prop: string, val: unknown): string {
  const propLower = (formatPropertyName(prop) || prop).toLowerCase()
  if (propLower === 'author') return formatAuthor(val)
  return formatValue(val)
}

function toAuthorDisplayItem(person: unknown): AuthorDisplayItem | null {
  if (person == null || typeof person !== 'object') return null
  const p = person as Record<string, unknown>
  const given = (p.givenName ?? p.given_name ?? '') as string
  const family = (p.familyName ?? p.family_name ?? '') as string
  const name = ((p.name as string) ?? [given, family].filter(Boolean).join(' ').trim()) || null
  const fullName = (name && name.trim() ? name : [given, family].filter(Boolean).join(' ').trim()) || ''
  if (!fullName) return null
  let url: string | undefined
  const rawId = (p['@id'] ?? p.id ?? '') as string
  if (rawId && typeof rawId === 'string' && rawId.trim()) {
    url = /^https?:\/\//i.test(rawId) ? rawId : (rawId.startsWith('orcid.org') ? `https://${rawId}` : rawId)
  }
  return { name: fullName, ...(url ? { url } : {}) }
}

function formatValue(val: unknown): string {
  if (val == null) return '—'
  if (typeof val === 'string') return val
  if (typeof val === 'number' || typeof val === 'boolean') return String(val)
  if (Array.isArray(val)) return val.map(v => formatValue(v)).join(', ')
  if (typeof val === 'object') return JSON.stringify(val)
  return String(val)
}

/** Format author (Person or array of Person) as readable "Full Name (ID)" lines, no JSON. */
function formatAuthor(val: unknown): string {
  if (val == null) return '—'
  if (Array.isArray(val)) {
    const lines = val.map(item => formatOneAuthor(item)).filter(Boolean)
    return lines.length ? lines.join('\n') : '—'
  }
  if (typeof val === 'object' && val !== null) return formatOneAuthor(val as Record<string, unknown>)
  return formatValue(val)
}

function formatOneAuthor(person: unknown): string {
  if (person == null || typeof person !== 'object') return ''
  const p = person as Record<string, unknown>
  const given = (p.givenName ?? p.given_name ?? '') as string
  const family = (p.familyName ?? p.family_name ?? '') as string
  const name = ((p.name as string) ?? [given, family].filter(Boolean).join(' ').trim()) || null
  const fullName = (name && name.trim() ? name : [given, family].filter(Boolean).join(' ').trim()) || ''
  if (!fullName) return ''

  let id = (p['@id'] ?? p.id ?? '') as string
  if (id && typeof id === 'string' && !/^https?:\/\//i.test(id)) id = id.startsWith('orcid.org') ? `https://${id}` : id

  if (id && typeof id === 'string' && id.trim()) return `${fullName} (${id})`
  return fullName
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
