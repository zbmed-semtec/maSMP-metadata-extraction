<template>
  <button
    :type="type"
    :disabled="disabled"
    :class="[
      'btn',
      variant === 'primary' ? 'btn-primary' : 'btn-secondary',
      size === 'small'
        ? 'px-3 py-1.5 text-sm'
        : size === 'large'
          ? 'px-6 py-3 text-lg'
          : '',
      disabled ? 'opacity-50 cursor-not-allowed' : '',
      customClass,
    ]"
    @click="$emit('click', $event)"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
type ButtonType = 'button' | 'submit' | 'reset'
type ButtonVariant = 'primary' | 'secondary'
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

