<template>
  <div class="min-h-screen bg-white">
    <!-- Hero Section -->
    <section class="py-12 sm:py-16 lg:py-20 xl:py-24">
      <div class="container-custom">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-16 items-start">
          <!-- Left Section: Application Info -->
          <div class="flex flex-col justify-center space-y-6">
            <div>
              <h1 class="text-4xl sm:text-5xl lg:text-6xl font-bold text-secondary-800 mb-4 leading-tight">
                CoMET-RS
              </h1>
              <p class="text-xl sm:text-2xl text-primary-600 mb-4 font-semibold">
                Code Metadata Extraction Tool for Research Software
              </p>
            </div>
            
            <p class="text-lg text-gray-600 leading-relaxed">
              Automatically extract comprehensive metadata from code repositories to generate 
              machine-actionable Software Management Plans (maSMP) and CodeMeta schemas.
            </p>
            
            <div class="pt-2">
              <NuxtLink
                to="/dashboard"
                class="btn-primary text-lg px-10 py-4 inline-block shadow-lg hover:shadow-xl transition-shadow"
              >
                Get Started
              </NuxtLink>
            </div>
          </div>

          <!-- Right Section: Platform Integration Carousel -->
          <div class="w-full">
            <PlatformCarousel v-model="currentPlatform" :platforms="platforms" />
          </div>
        </div>
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
  {
    name: 'Zenodo',
    logo: null,
    active: false,
  },
]
</script>
