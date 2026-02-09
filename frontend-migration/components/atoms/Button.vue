<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="[
      'btn',
      variant === 'primary' ? 'btn-primary' : 
      variant === 'accent' ? 'btn-accent' : 'btn-secondary',
      size === 'small'
        ? 'px-3 py-1.5 text-xs sm:text-sm'
        : size === 'large'
          ? 'px-5 py-2.5 sm:px-6 sm:py-3 text-base sm:text-lg'
          : '',
      customClass,
    ]"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
type ButtonType = 'button' | 'submit' | 'reset'
type ButtonVariant = 'primary' | 'secondary' | 'accent'
type ButtonSize = 'small' | 'medium' | 'large'

interface Props {
  type?: ButtonType
  variant?: ButtonVariant
  size?: ButtonSize
  disabled?: boolean
  customClass?: string
}

withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  size: 'medium',
  disabled: false,
  customClass: '',
})

defineEmits<{
  (e: 'click', event: MouseEvent): void
}>()
</script>

