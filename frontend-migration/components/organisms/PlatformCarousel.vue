<template>
  <div 
    class="rounded-xl border border-gray-200 bg-white shadow-sm p-5 sm:p-6 h-full flex flex-col"
    @mouseenter="pauseAutoPlay"
    @mouseleave="resumeAutoPlay"
  >
    <h2 class="text-xl sm:text-2xl font-bold text-secondary-800 mb-4 sm:mb-5">
      Integrated Platforms
    </h2>
    
    <!-- Logo Display Area -->
    <div class="relative flex items-center justify-center mb-4 sm:mb-5 h-28 sm:h-32 md:h-36 bg-gray-50 rounded-lg border border-gray-100">
      <CarouselNavButton
        direction="prev"
        size="large"
        position="left"
        aria-label="Previous platform"
        @click="handlePrevious"
      />

      <div class="flex-1 flex items-center justify-center px-8 sm:px-12 md:px-16">
        <img
          v-if="platforms[currentIndex].logo"
          :src="platforms[currentIndex].logo"
          :alt="platforms[currentIndex].name"
          :class="[
            'h-14 sm:h-16 md:h-20 w-auto transition-all duration-300 max-w-[140px] sm:max-w-[160px] md:max-w-[180px] object-contain',
            platforms[currentIndex].name === 'GitLab' ? 'max-w-[100px] sm:max-w-[120px] md:max-w-[140px]' : '',
            platforms[currentIndex].active ? 'opacity-100' : 'opacity-60'
          ]"
        />
        <div
          v-else
          :class="[
            'h-16 sm:h-20 md:h-24 w-28 sm:w-36 md:w-40 bg-gray-200 rounded-lg flex items-center justify-center transition-all duration-300',
            platforms[currentIndex].active ? 'opacity-100' : 'opacity-50'
          ]"
        >
          <span :class="[
            'text-gray-600 font-semibold text-xs sm:text-sm md:text-base',
            platforms[currentIndex].active ? '' : 'opacity-60'
          ]">
            {{ platforms[currentIndex].name }}
          </span>
        </div>
      </div>

      <CarouselNavButton
        direction="next"
        size="large"
        position="right"
        aria-label="Next platform"
        @click="handleNext"
      />
    </div>

    <!-- Platform List -->
    <div class="relative">
      <CarouselNavButton
        direction="prev"
        size="small"
        position="left"
        aria-label="Scroll left"
        @click="scrollList(-1)"
      />

      <div 
        class="flex items-center justify-center gap-2 sm:gap-3 overflow-x-auto px-8 sm:px-10 scrollbar-hide touch-pan-x" 
        ref="platformListRef"
      >
        <PlatformButton
          v-for="(platform, index) in platforms"
          :key="platform.name"
          :platform-name="platform.name"
          :is-active="currentIndex === index"
          :is-integrated="platform.active"
          @click="handlePlatformClick(index)"
        />
      </div>

      <CarouselNavButton
        direction="next"
        size="small"
        position="right"
        aria-label="Scroll right"
        @click="scrollList(1)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

interface Platform {
  name: string
  logo: string | null
  active: boolean
}

interface Props {
  platforms: Platform[]
  autoPlayInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  autoPlayInterval: 3000,
})

const currentIndex = defineModel<number>({ default: 0 })
const platformListRef = ref<HTMLElement | null>(null)
let autoPlayInterval: ReturnType<typeof setInterval> | null = null

const next = () => {
  currentIndex.value = (currentIndex.value + 1) % props.platforms.length
}

const previous = () => {
  currentIndex.value = currentIndex.value === 0 ? props.platforms.length - 1 : currentIndex.value - 1
}

const handleNext = () => {
  next()
  pauseAutoPlay()
  setTimeout(resumeAutoPlay, 5000)
}

const handlePrevious = () => {
  previous()
  pauseAutoPlay()
  setTimeout(resumeAutoPlay, 5000)
}

const handlePlatformClick = (index: number) => {
  currentIndex.value = index
  pauseAutoPlay()
  setTimeout(resumeAutoPlay, 5000)
}

const scrollList = (direction: number) => {
  if (platformListRef.value) {
    const scrollAmount = 200
    platformListRef.value.scrollBy({
      left: scrollAmount * direction,
      behavior: 'smooth',
    })
  }
}

const startAutoPlay = () => {
  autoPlayInterval = setInterval(() => {
    next()
  }, props.autoPlayInterval)
}

const pauseAutoPlay = () => {
  if (autoPlayInterval) {
    clearInterval(autoPlayInterval)
    autoPlayInterval = null
  }
}

const resumeAutoPlay = () => {
  if (!autoPlayInterval) {
    startAutoPlay()
  }
}

onMounted(() => {
  startAutoPlay()
})

onUnmounted(() => {
  pauseAutoPlay()
})
</script>
