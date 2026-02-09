<template>
  <nav class="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
    <div class="container-custom">
      <div class="flex items-center justify-between h-14 sm:h-16">
        <Logo />

        <!-- Desktop navigation -->
        <div class="hidden md:flex items-center space-x-1">
          <NuxtLink
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="px-3 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium transition-colors"
            :class="
              isActive(item.path)
                ? 'bg-primary-100 text-primary-700'
                : 'text-secondary-700 hover:bg-primary-50 hover:text-primary-600'
            "
          >
            {{ item.label }}
          </NuxtLink>
        </div>

        <!-- Mobile menu button -->
        <button
          type="button"
          class="md:hidden p-2 rounded-lg text-secondary-700 hover:bg-primary-50"
          aria-label="Toggle menu"
          @click="mobileMenuOpen = !mobileMenuOpen"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              v-if="!mobileMenuOpen"
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

      <!-- Mobile navigation -->
      <div
        v-if="mobileMenuOpen"
        class="md:hidden py-4 border-t border-gray-200"
      >
        <NuxtLink
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="block px-4 py-2.5 rounded-lg text-sm font-medium transition-colors touch-manipulation"
          :class="
            isActive(item.path)
              ? 'bg-primary-100 text-primary-700'
              : 'text-secondary-700 hover:bg-primary-50 hover:text-primary-600'
          "
          @click="mobileMenuOpen = false"
        >
          {{ item.label }}
        </NuxtLink>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
const route = useRoute()
const mobileMenuOpen = ref(false)

const navItems = [
  { path: '/', label: 'Home' },
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/fair-assessment', label: 'FAIR Assessment' },
  { path: '/best-practices', label: 'Best Practices' },
]

const isActive = (path: string) => {
  if (path === '/') {
    return route.path === '/'
  }
  return route.path.startsWith(path)
}
</script>

