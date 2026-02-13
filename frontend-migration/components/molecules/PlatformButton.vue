<template>
  <button
    :class="[
      'px-3 py-2 sm:px-4 sm:py-2.5 md:px-5 rounded-lg text-xs sm:text-sm font-semibold whitespace-nowrap transition-all duration-200 touch-manipulation',
      isActive
        ? 'bg-primary-500 text-white shadow-lg scale-105'
        : isIntegrated
          ? 'bg-white text-gray-700 hover:bg-gray-100 active:bg-gray-200 border border-gray-200'
          : 'bg-gray-200 text-gray-500 opacity-60 hover:opacity-80 active:opacity-90'
    ]"
    @click="$emit('click')"
  >
    {{ platformName }}
  </button>
</template>

<script setup lang="ts">
interface Props {
  platformName: string
  isActive: boolean
  isIntegrated: boolean
}

defineProps<Props>()

defineEmits<{
  (e: 'click'): void
}>()
</script>
