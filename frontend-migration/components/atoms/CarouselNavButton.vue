<template>
  <button
    :class="[
      'rounded-full bg-white flex items-center justify-center hover:bg-gray-50 active:bg-gray-100 hover:border-primary-400 transition-all z-10 touch-manipulation',
      size === 'large' 
        ? 'w-10 h-10 sm:w-12 sm:h-12 border-2 border-gray-300 shadow-md' 
        : 'w-7 h-7 sm:w-8 sm:h-8 border border-gray-300 shadow-sm',
      position === 'left' 
        ? size === 'large' ? 'absolute left-1 sm:left-2' : 'absolute left-0 top-1/2 -translate-y-1/2'
        : position === 'right'
          ? size === 'large' ? 'absolute right-1 sm:right-2' : 'absolute right-0 top-1/2 -translate-y-1/2'
          : ''
    ]"
    :aria-label="ariaLabel"
    @click="$emit('click')"
  >
    <svg 
      :class="size === 'large' ? 'w-5 h-5 sm:w-6 sm:h-6' : 'w-3.5 h-3.5 sm:w-4 sm:h-4'"
      class="text-gray-700" 
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      <path 
        v-if="direction === 'prev'"
        stroke-linecap="round" 
        stroke-linejoin="round" 
        stroke-width="2" 
        d="M15 19l-7-7 7-7" 
      />
      <path 
        v-else
        stroke-linecap="round" 
        stroke-linejoin="round" 
        stroke-width="2" 
        d="M9 5l7 7-7 7" 
      />
    </svg>
  </button>
</template>

<script setup lang="ts">
interface Props {
  direction: 'prev' | 'next'
  size?: 'small' | 'large'
  position?: 'left' | 'right' | 'none'
  ariaLabel?: string
}

withDefaults(defineProps<Props>(), {
  size: 'small',
  position: 'none',
  ariaLabel: 'Navigate',
})

defineEmits<{
  (e: 'click'): void
}>()
</script>
