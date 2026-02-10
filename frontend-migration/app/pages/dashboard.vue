<template>
  <div class="min-h-full bg-gray-50 py-6 sm:py-8">
    <div class="container-custom w-full">
      <Card padding="p-6 sm:p-8" custom-class="rounded-xl">
        <form class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-5" @submit.prevent="onExtract">
          <!-- Row 1: Repository URL | Schema -->
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

          <!-- Row 2: Access token | Extract button -->
          <div class="relative">
            <label for="access-token" class="label block text-sm font-medium text-secondary-800 mb-1.5">
              Access token
              <button
                type="button"
                aria-label="How to get a GitHub access token"
                class="inline-flex items-center justify-center w-4 h-4 ml-1 rounded-full border border-gray-300 bg-gray-50 text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-1 align-middle"
                @click="showTokenTip = !showTokenTip"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-3.5 h-3.5">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9.879 7.519c1.171-1.025 3.071-1.025 4.242 0 1.172 1.025 1.172 2.687 0 3.712-.203.179-.43.326-.67.442-.745.361-1.45.999-1.45 1.827v.75M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9 5.25h.008v.008H12v-.008z" />
                </svg>
              </button>
            </label>
            <Input
              id="access-token"
              v-model="accessToken"
              type="password"
              placeholder="Optional for public repos"
            />

            <!-- Info tip popover -->
            <Teleport to="body">
              <div
                v-if="showTokenTip"
                class="fixed inset-0 z-40 bg-black/20"
                aria-hidden="true"
                @click="showTokenTip = false"
              />
              <div
                v-if="showTokenTip"
                class="fixed z-50 w-[calc(100vw-2rem)] max-w-sm top-1/2 -translate-y-1/2 left-4 right-4 sm:left-1/2 sm:right-auto sm:-translate-x-1/2 rounded-xl border border-gray-200 bg-white shadow-xl"
                role="dialog"
                aria-labelledby="token-tip-title"
                @click.stop
              >
                <div class="flex items-center justify-between gap-3 border-b border-gray-100 px-4 py-3 bg-gray-50/80 rounded-t-xl">
                  <h3 id="token-tip-title" class="text-sm font-semibold text-secondary-800">
                    GitHub access token
                  </h3>
                  <button
                    type="button"
                    aria-label="Close"
                    class="p-1 rounded-md text-gray-400 hover:text-gray-600 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-primary-500"
                    @click="showTokenTip = false"
                  >
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <div class="p-4 max-h-[60vh] overflow-y-auto">
                  <p class="text-sm text-gray-600 mb-3 leading-relaxed">
                    Required for private repos; recommended for public repos to avoid API limits.
                  </p>
                  <p class="text-xs font-medium text-secondary-800 uppercase tracking-wide mb-2">
                    How to get one
                  </p>
                  <ol class="list-decimal list-inside text-sm text-gray-600 space-y-1.5 leading-relaxed">
                    <li>Go to <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" class="text-primary-600 hover:text-primary-700 underline underline-offset-1">GitHub Developer Settings</a></li>
                    <li>Click <strong class="text-gray-800">"Generate new token (classic)"</strong></li>
                    <li>Set <strong class="text-gray-800">expiration</strong> (optional)</li>
                    <li>Enable scopes: <strong class="text-gray-800">repo</strong> (private repos), <strong class="text-gray-800">read:org</strong> (org repos)</li>
                    <li>Click <strong class="text-gray-800">"Generate token"</strong></li>
                    <li>Copy and store it securely, it won’t be shown again.</li>
                  </ol>
                </div>
              </div>
            </Teleport>
          </div>

          <div class="flex items-end">
            <Button
              type="submit"
              :disabled="isLoading"
              custom-class="w-full"
            >
              {{ isLoading ? 'Extracting…' : 'Extract' }}
            </Button>
          </div>

          <p v-if="error" class="text-sm text-red-600 sm:col-span-2">
            {{ error }}
          </p>
        </form>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useApi } from '../../composables/useApi'

const repoUrl = ref('')
const schema = ref<'maSMP' | 'CodeMeta'>('maSMP')
const accessToken = ref('')
const isLoading = ref(false)
const error = ref('')
const showTokenTip = ref(false)

useHead({
  title: 'Extract metadata - CoMET-RS',
})

const onExtract = async () => {
  error.value = ''
  isLoading.value = true
  try {
    const { extractMetadata } = useApi()
    const { data, error: err } = await extractMetadata(
      repoUrl.value,
      schema.value,
      accessToken.value || undefined
    )
    if (err) {
      error.value = err
      return
    }
    // TODO: show results (e.g. navigate to results or display in same page)
    if (data) {
      // placeholder: could set result state or navigate
    }
  } finally {
    isLoading.value = false
  }
}
</script>
