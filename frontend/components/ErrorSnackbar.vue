<template>
    <v-snackbar v-model="show" color="error" timeout="1500">
      {{ errorMessage }}
      <template v-slot:actions>
        <v-btn color="white" variant="text" @click="$emit('close')">
          Close
        </v-btn>
      </template>
    </v-snackbar>
  </template>
  
  <script setup>
  defineProps(['value', 'errorMessage'])
  defineEmits(['close', 'update:value'])
  </script>