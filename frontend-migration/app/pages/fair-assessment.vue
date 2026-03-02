<template>
  <div class="min-h-full bg-gray-50 py-6 sm:py-8">
    <div class="container-custom w-full space-y-6">
      <Card padding="p-6 sm:p-8" custom-class="rounded-xl">
        <form class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5" @submit.prevent="onAssess">
          <div>
            <Input
              id="repo-url"
              v-model="repoUrl"
              type="url"
              required
              label="Repository URL"
              placeholder="https://github.com/owner/repo"
            />
          </div>

          <div>
            <label for="schema" class="label block text-sm font-medium text-secondary-800 mb-1.5">
              Schema
            </label>
            <select
              id="schema"
              v-model="schema"
              class="input-field w-full rounded-lg border border-gray-300 bg-white px-3 py-2.5 text-secondary-800 focus:border-primary-500 focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              <option value="maSMP">maSMP</option>
              <option value="CodeMeta">CodeMeta</option>
            </select>
          </div>

          <div>
            <Input
              id="access-token"
              v-model="accessToken"
              type="password"
              label="Access token"
              placeholder="Optional for public repos"
            />
          </div>

          <div class="flex items-end">
            <Button
              type="submit"
              :disabled="isLoading"
              custom-class="w-full"
            >
              {{ isLoading ? 'Assessing…' : 'Assess FAIRness' }}
            </Button>
          </div>

          <p v-if="error" class="text-sm text-red-600 sm:col-span-2">
            {{ error }}
          </p>
        </form>
      </Card>

      <Card
        v-if="fairness && !isLoading"
        padding="p-6 sm:p-8"
        custom-class="rounded-xl space-y-6"
      >
        <div class="mb-4 space-y-1">
          <h2 class="text-lg sm:text-xl font-semibold text-secondary-800">
            FAIRness summary
          </h2>
          <p class="mt-1 text-sm text-gray-600">
            Overall FAIRness score and per-principle scores for the selected repository.
          </p>
          <p class="mt-1 text-xs text-gray-500">
            Based on FAIRness indicators derived from 10 FAIR best practices for research software
            (description, identifier, download URL, versioning, documentation, license, citation,
            metadata, installation, requirements).
          </p>
        </div>
        <div class="grid grid-cols-2 sm:grid-cols-5 gap-4 mb-4">
          <div class="rounded-lg border border-gray-200 bg-white px-4 py-3 text-center">
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">
              Overall
            </p>
            <p class="text-xl font-semibold text-primary-600">
              {{ (fairness.overall_score * 100).toFixed(0) }}%
            </p>
          </div>
          <div class="rounded-lg border border-gray-200 bg-white px-4 py-3 text-center">
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">
              Findable
            </p>
            <p class="text-xl font-semibold text-primary-600">
              {{ (fairness.findable * 100).toFixed(0) }}%
            </p>
          </div>
          <div class="rounded-lg border border-gray-200 bg-white px-4 py-3 text-center">
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">
              Accessible
            </p>
            <p class="text-xl font-semibold text-primary-600">
              {{ (fairness.accessible * 100).toFixed(0) }}%
            </p>
          </div>
          <div class="rounded-lg border border-gray-200 bg-white px-4 py-3 text-center">
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">
              Interoperable
            </p>
            <p class="text-xl font-semibold text-primary-600">
              {{ (fairness.interoperable * 100).toFixed(0) }}%
            </p>
          </div>
          <div class="rounded-lg border border-gray-200 bg-white px-4 py-3 text-center">
            <p class="text-xs uppercase tracking-wide text-gray-500 mb-1">
              Reusable
            </p>
            <p class="text-xl font-semibold text-primary-600">
              {{ (fairness.reusable * 100).toFixed(0) }}%
            </p>
          </div>
        </div>

        <div v-if="groupedIndicators" class="space-y-6">
          <section v-if="groupedIndicators.documentation.length">
            <h3 class="text-sm font-semibold text-secondary-800 mb-3">
              Documentation &amp; governance
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <FairnessIndicatorDonut
                v-for="indicator in groupedIndicators.documentation"
                :key="indicator.id"
                :indicator="indicator"
              />
            </div>
          </section>

          <section v-if="groupedIndicators.findability.length">
            <h3 class="text-sm font-semibold text-secondary-800 mb-3">
              Findability &amp; metadata
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <FairnessIndicatorDonut
                v-for="indicator in groupedIndicators.findability"
                :key="indicator.id"
                :indicator="indicator"
              />
            </div>
          </section>

          <section v-if="groupedIndicators.access.length">
            <h3 class="text-sm font-semibold text-secondary-800 mb-3">
              Access &amp; releases
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              <FairnessIndicatorDonut
                v-for="indicator in groupedIndicators.access"
                :key="indicator.id"
                :indicator="indicator"
              />
            </div>
          </section>
        </div>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useApi } from '../../composables/useApi'
import { useFairnessStore } from '../../stores/fairness'
import { useExtractionStore } from '../../stores/extraction'

const extractionStore = useExtractionStore()
const fairnessStore = useFairnessStore()

// Reuse the same inputs as the Extract Metadata page
const repoUrl = computed({
  get: () => extractionStore.repoUrl,
  set: (v: string) => {
    extractionStore.repoUrl = v
  },
})

const schema = computed<'maSMP' | 'CodeMeta'>({
  get: () => extractionStore.schema,
  set: (v) => {
    extractionStore.schema = v
  },
})

const accessToken = computed({
  get: () => extractionStore.accessToken,
  set: (v: string) => {
    extractionStore.accessToken = v
  },
})

const isLoading = ref(false)
const error = computed({
  get: () => fairnessStore.error,
  set: (v: string) => {
    fairnessStore.error = v
  },
})
const fairness = computed<any | null>({
  get: () => fairnessStore.fairness,
  set: (v) => {
    fairnessStore.fairness = v
  },
})

const groupedIndicators = computed(() => {
  const indicators = (fairness.value?.indicators || []) as any[]
  const byIds = (ids: string[]) => indicators.filter((i) => ids.includes(i.id))
  return {
    documentation: byIds([
      'bp1_description_present',
      'bp5_usage_documentation',
      'bp6_license_declared',
      'bp7_explicit_citation',
      'bp9_install_instructions',
      'bp10_software_requirements',
    ]),
    findability: byIds([
      'bp2_persistent_identifier',
      'bp8_software_metadata',
    ]),
    access: byIds([
      'bp3_download_url_available',
      'bp4_semver_like_version',
    ]),
  }
})

useHead({
  title: 'FAIR Assessment - CoMET-RS',
})

const onAssess = async () => {
  error.value = ''
  fairness.value = null
  isLoading.value = true
  try {
    const { getFairness } = useApi()
    const { data, error: apiError } = await getFairness(
      repoUrl.value,
      schema.value,
      accessToken.value || undefined
    )
    if (apiError) {
      error.value = apiError
    } else if (data && (data as any).fairness) {
      fairnessStore.setForm(repoUrl.value, schema.value, accessToken.value)
      fairnessStore.setFairness((data as any).fairness)
    } else {
      error.value = 'No FAIRness data returned.'
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'FAIRness assessment failed'
  } finally {
    isLoading.value = false
  }
}

// When navigating to the FAIR Assessment page, automatically
// run FAIRness assessment if we already have input from the
// Extract Metadata page but no FAIRness result yet.
onMounted(async () => {
  if (!repoUrl.value) {
    return
  }
  if (fairness.value) {
    return
  }
  await onAssess()
})
</script>