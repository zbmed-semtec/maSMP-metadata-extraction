import { defineStore } from 'pinia'
import type { ExtractionStreamResult } from '../composables/useApi'

type SchemaType = 'maSMP' | 'CodeMeta'

interface ExtractionState {
  repoUrl: string
  schema: SchemaType
  accessToken: string
  result: ExtractionStreamResult | null
  error: string
}

export const useExtractionStore = defineStore('extraction', {
  state: (): ExtractionState => ({
    repoUrl: '',
    schema: 'maSMP',
    accessToken: '',
    result: null,
    error: '',
  }),
  actions: {
    setForm(repoUrl: string, schema: SchemaType, accessToken: string) {
      this.repoUrl = repoUrl
      this.schema = schema
      this.accessToken = accessToken
    },
    setResult(result: ExtractionStreamResult | null) {
      this.result = result
    },
    setError(message: string) {
      this.error = message
    },
    clear() {
      this.result = null
      this.error = ''
    },
  },
})

