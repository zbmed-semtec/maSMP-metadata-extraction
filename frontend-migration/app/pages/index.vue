<template>
  <div class="min-h-full flex flex-col bg-gray-50">
    <!-- Hero Section: two matching cards -->
    <section class="shrink-0 pt-5 pb-8 sm:pt-6 sm:pb-10">
      <div class="container-custom">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 lg:gap-8 items-stretch">
          <!-- Left card: less space above heading, more below button -->
          <div class="rounded-xl border border-gray-200 bg-white shadow-sm flex flex-col pt-4 px-5 pb-6 sm:pt-5 sm:px-6 sm:pb-7">
            <h1 class="text-xl sm:text-2xl font-bold text-secondary-800 tracking-tight mb-2.5">
              About CoMET-RS
            </h1>
            <p class="text-gray-600 text-sm sm:text-base leading-relaxed mb-4">
              The Code Metadata Extraction Tool for Research Software (CoMET-RS) is a web application that automatically extracts metadata from a code repository and displays it in a user-friendly interface. 
            </p>
            <p class="text-gray-600 text-sm sm:text-base leading-relaxed mb-4">
              It generates metadata conforming to machine-actionable Software Management Plans (maSMPs) and CodeMeta schemas, helping standardize documentation, improve interoperability, and reduce maintenance effort.
            </p>
            <NuxtLink
              to="/dashboard"
              class="inline-flex items-center gap-2 rounded-lg bg-primary-500 px-6 py-2.5 text-sm font-medium text-white shadow-sm transition-all hover:bg-primary-600 hover:shadow w-fit"
            >
              Get Started
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </NuxtLink>
          </div>

          <!-- Right card: same style as left -->
          <div class="w-full min-h-[200px]">
            <PlatformCarousel v-model="currentPlatform" :platforms="platforms" />
          </div>
        </div>
      </div>
    </section>

    <!-- Extraction pipeline: uses remaining space, centered -->
    <section class="flex-1 flex flex-col justify-center px-4 pb-8 sm:pb-10">
      <div class="container-custom">
        <ExtractionPipeline />
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

useHead({
  title: 'CoMET-RS - Code Metadata Extraction Tool for Research Software',
  meta: [
    {
      name: 'description',
      content: 'Automatically extract comprehensive metadata from code repositories to generate machine-actionable Software Management Plans (SMP) and CodeMeta schemas.',
    },
  ],
})

const currentPlatform = ref(0)

const platforms = [
  {
    name: 'GitHub',
    logo: '/Github_logo.png',
    active: true,
  },
  {
    name: 'GitLab',
    logo: '/Gitlab_logo.png',
    active: true,
  },
  {
    name: 'Codeberg',
    logo: '/Codeberg_logo.png',
    active: false,
  },
]
</script>
