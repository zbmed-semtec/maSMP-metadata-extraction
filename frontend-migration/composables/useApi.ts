// composables/useApi.ts
import axios from 'axios'

// Local declaration so TypeScript recognizes Nuxt's runtime config helper
declare function useRuntimeConfig(): {
  public: {
    apiBase: string
  }
}

export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const api = axios.create({
    baseURL: apiBase,
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const extractMetadata = async (
    repoUrl: string,
    schema: string = 'maSMP',
    accessToken?: string
  ) => {
    try {
      const response = await api.get('/metadata', {
        params: {
          repo_url: repoUrl,
          schema,
          access_token: accessToken
        }
      })
      return { data: response.data, error: null }
    } catch (error: any) {
      return {
        data: null,
        error:
          error.response?.data?.detail ||
          error.message ||
          'An error occurred while extracting metadata'
      }
    }
  }

  return {
    api,
    extractMetadata
  }
}
