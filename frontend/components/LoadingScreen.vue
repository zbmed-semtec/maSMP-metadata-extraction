<template>
    <v-overlay :model-value="isLoading" scrim="black" class="loading-overlay">
      <v-progress-circular indeterminate color="primary" size="64" />
      <p class="mt-4 text-white">Loading...</p>
    </v-overlay>
  </template>
  
  <script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  
  const isLoading = ref(true)
  
  const handleLoad = () => {
    isLoading.value = false
  }
  
  onMounted(() => {
    window.addEventListener('load', handleLoad)
  })
  
  onUnmounted(() => {
    window.removeEventListener('load', handleLoad)
  })
  </script>
  
  <style scoped>
  .loading-overlay {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  </style>