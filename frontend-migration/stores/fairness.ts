import { defineStore } from 'pinia'

type SchemaType = 'maSMP' | 'CodeMeta'

interface FairnessState {
  repoUrl: string
  schema: SchemaType
  accessToken: string
  fairness: any | null
  error: string
}

export const useFairnessStore = defineStore('fairness', {
  state: (): FairnessState => ({
    repoUrl: '',
    schema: 'maSMP',
    accessToken: '',
    fairness: null,
    error: '',
  }),
  actions: {
    setForm(repoUrl: string, schema: SchemaType, accessToken: string) {
      this.repoUrl = repoUrl
      this.schema = schema
      this.accessToken = accessToken
    },
    setFairness(fairness: any | null) {
      this.fairness = fairness
    },
    setError(message: string) {
      this.error = message
    },
    clear() {
      this.fairness = null
      this.error = ''
    },
  },
})

