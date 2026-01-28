<template>
  <div :class="['card', padding, customClass]">
    <div
      v-if="title || $slots.header"
      class="mb-4 pb-4 border-b border-gray-200"
    >
      <slot name="header">
        <h3
          v-if="title"
          class="text-lg font-semibold text-gray-900"
        >
          {{ title }}
        </h3>
      </slot>
    </div>

    <div>
      <slot />
    </div>

    <div
      v-if="$slots.footer"
      class="mt-4 pt-4 border-t border-gray-200"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  padding?: string
  customClass?: string
}

withDefaults(defineProps<Props>(), {
  padding: 'p-6',
  customClass: '',
})
</script>

