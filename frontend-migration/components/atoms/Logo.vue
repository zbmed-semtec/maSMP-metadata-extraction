<template>
  <NuxtLink
    to="/"
    class="flex items-center gap-2 font-bold text-lg sm:text-xl shrink-0 transition-opacity hover:opacity-90"
    :class="inverted ? 'text-white hover:text-cyan-200' : 'text-secondary-800'"
  >
    <img
      src="/COMET-RS.png"
      alt="CoMET-RS"
      :class="['w-auto', inverted ? 'h-10 sm:h-12 brightness-0 invert' : 'h-10 sm:h-12']"
    />
    <div v-if="!inverted" class="flex flex-col">
      <span>CoMET-RS</span>
      <span class="text-xs sm:text-sm text-gray-600 hidden sm:block font-normal">maSMP Metadata Extractor</span>
    </div>
    <span v-else>CoMET-RS</span>
  </NuxtLink>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{ inverted?: boolean }>(),
  { inverted: false }
)
</script>

