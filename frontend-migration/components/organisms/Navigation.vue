<template>
  <header class="bg-secondary-800 text-white sticky top-0 z-50 shadow-md">
    <div class="container-custom">
      <div class="flex items-center justify-between h-14 sm:h-16">
        <NuxtLink
          to="/"
          class="flex items-center gap-2 font-bold text-lg sm:text-xl text-white hover:text-cyan-200 transition-colors shrink-0"
        >
          <span>CoMET-RS</span>
        </NuxtLink>

        <!-- Desktop nav: all 4 links visible from md up -->
        <nav class="hidden md:flex items-center gap-1 sm:gap-2">
          <NuxtLink
            to="/"
            class="px-3 sm:px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 hover:text-white transition-colors"
            :class="{ 'bg-white/15 text-white': route.path === '/' }"
          >
            Home
          </NuxtLink>
          <NuxtLink
            to="/dashboard"
            class="px-3 sm:px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 hover:text-white transition-colors"
            :class="{ 'bg-white/15 text-white': route.path.startsWith('/dashboard') }"
          >
            Extract Metadata
          </NuxtLink>
          <NuxtLink
            to="/fair-assessment"
            class="px-3 sm:px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 hover:text-white transition-colors"
            :class="{ 'bg-white/15 text-white': route.path.startsWith('/fair-assessment') }"
          >
            FAIR Assessment
          </NuxtLink>
          <NuxtLink
            to="/best-practices"
            class="px-3 sm:px-4 py-2 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 hover:text-white transition-colors"
            :class="{ 'bg-white/15 text-white': route.path.startsWith('/best-practices') }"
          >
            Best Practices
          </NuxtLink>
        </nav>

        <!-- Mobile: hamburger button -->
        <button
          type="button"
          class="md:hidden p-2 rounded-lg text-white hover:bg-white/10 transition-colors"
          aria-label="Open menu"
          :aria-expanded="menuOpen"
          @click="menuOpen = !menuOpen"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            aria-hidden="true"
          >
            <path
              v-if="!menuOpen"
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M4 6h16M4 12h16M4 18h16"
            />
            <path
              v-else
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>

      <!-- Mobile dropdown: all 4 links when menu is open -->
      <div
        v-show="menuOpen"
        class="md:hidden py-3 border-t border-white/20"
      >
        <nav class="flex flex-col gap-1">
          <NuxtLink
            to="/"
            class="px-4 py-3 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 transition-colors"
            :class="{ 'bg-white/15 text-white': route.path === '/' }"
            @click="menuOpen = false"
          >
            Home
          </NuxtLink>
          <NuxtLink
            to="/dashboard"
            class="px-4 py-3 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 transition-colors"
            :class="{ 'bg-white/15 text-white': route.path.startsWith('/dashboard') }"
            @click="menuOpen = false"
          >
            Extract Metadata
          </NuxtLink>
          <NuxtLink
            to="/fair-assessment"
            class="px-4 py-3 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 transition-colors"
            :class="{ 'bg-white/15 text-white': route.path.startsWith('/fair-assessment') }"
            @click="menuOpen = false"
          >
            FAIR Assessment
          </NuxtLink>
          <NuxtLink
            to="/best-practices"
            class="px-4 py-3 rounded-lg text-sm font-medium text-white/90 hover:bg-white/10 transition-colors"
            :class="{ 'bg-white/15 text-white': route.path.startsWith('/best-practices') }"
            @click="menuOpen = false"
          >
            Best Practices
          </NuxtLink>
        </nav>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
const route = useRoute()
const menuOpen = ref(false)
</script>
