<template>
  <v-card elevation="8" rounded="l" style="background-color: #f5f7ff;">
    <v-form @submit.prevent="$emit('validateAndExtract')" autocomplete="off">
      <v-container>
        <v-row>
          <v-col cols="12" md="6">
            <v-text-field 
              color="#1f78b4"
              :value="githubUrl"
              label="GitHub URL"
              required
              :error-messages="githubUrlError"
              autocomplete="off"
              @update:modelValue="$emit('update:githubUrl', $event)"
              >
            <template v-slot:prepend>
              <v-icon color="#1f78b4">mdi-github</v-icon>
            </template>
            </v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-text-field
              color="#1f78b4"
              :value="accessCode"
              label="Access Code (optional)"
              type="password"
              append-inner-icon="mdi-information-outline"
              @click:append-inner="$emit('showAccessTokenInfo')"
              autocomplete="off"
              @update:modelValue="$emit('update:accessCode', $event)"
            >
            <template v-slot:prepend>
              <v-icon color="#1f78b4">mdi-lock</v-icon>
            </template>
            </v-text-field>
          </v-col>

          <v-col cols="12" md="6">
            <v-select
              color="#1f78b4"
              :value="selectedSchema"
              :items="schemas"
              label="Select Schema"
              :error-messages="schemaError"
              @update:modelValue="$emit('update:selectedSchema', $event)"
              >
            <template v-slot:prepend>
              <v-icon color="#1f78b4">mdi-database</v-icon>
            </template>
            </v-select>
          </v-col>

          <v-col cols="12" md="6" class="d-flex align-center justify-end" style="gap: 1rem;">
            <v-btn color="#1f78b4" rounded="l" @click="$emit('validateAndExtract')">
              <v-icon start>mdi-database-export</v-icon>
              Extract Metadata
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-form>
  </v-card>
</template>

<script setup>
defineProps([
  'githubUrl',
  'accessCode',
  'selectedSchema',
  'schemas',
  'githubUrlError',
  'schemaError'
])

defineEmits([
  'update:githubUrl',
  'update:accessCode',
  'update:selectedSchema',
  'validateAndExtract',
  'showAccessTokenInfo'
])
</script>
