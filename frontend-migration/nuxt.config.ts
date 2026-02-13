// nuxt.config.ts
import { resolve } from 'path'

export default defineNuxtConfig({
  devtools: { enabled: true },
  // Enable the classic pages/ directory router so <NuxtPage> renders our pages
  pages: true,
  // Explicitly set Nitro compatibility date to silence Nuxt's warning
  compatibilityDate: '2026-01-28',
  
  modules: [
    '@nuxtjs/tailwindcss',
    '@pinia/nuxt'
  ],

  css: [resolve(__dirname, 'assets/css/main.css')],

  components: {
    dirs: [
      {
        // Use project-root components directory (not app/), to avoid redundant folders
        path: '~~/components/atoms',
        pathPrefix: false,
      },
      {
        path: '~~/components/molecules',
        pathPrefix: false,
      },
      {
        path: '~~/components/organisms',
        pathPrefix: false,
      },
    ],
  },

  app: {
    head: {
      title: 'maSMP Metadata Extractor',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: 'Machine-Actionable Software Management Plan Metadata Extraction' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
      ]
    }
  },

  runtimeConfig: {
    public: {
      apiBase: process.env.API_BASE_URL || 'http://127.0.0.1:8000'
    }
  },

  nitro: {
    // Keep nitro-specific config here (compatibilityDate is also set top-level)
    compatibilityDate: '2026-01-28'
  }
})