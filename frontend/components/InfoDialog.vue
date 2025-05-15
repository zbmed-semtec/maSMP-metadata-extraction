<template>
    <v-dialog v-model="show" max-width="600">
      <v-card class="bg-surface-light mx-auto my-8" variant="outlined" elevation="16">
        <v-card-title class="d-flex align-center">
          <v-icon class="mr-2" color="#000055">mdi-lock</v-icon>
          GitHub Access Token
        </v-card-title>
        <v-card-text class="text-body-2">
          <p class="mb-2">
            A GitHub access token is required for private repositories and recommended for public repositories to avoid hitting API limits.
          </p>
          <p class="font-weight-medium mb-2">How to Get a GitHub Access Token?</p>
          <ol class="pl-4">
            <li>
              Go to <a href="https://github.com/settings/tokens" target="_blank">GitHub Developer Settings</a>
            </li>
            <li>
              Click <strong>Generate new token (classic)</strong>
            </li>
            <li>
              Select expiration (optional, but recommended)
            </li>
            <li>
              Enable the following scopes:
              <ul class="pl-4">
                <li><code>repo</code> (for private repositories)</li>
                <li><code>read:org</code> (for organization repositories)</li>
              </ul>
            </li>
            <li>
              Click <strong>Generate token</strong>
            </li>
            <li>
              <strong>Copy the token</strong> and store it securely (it won't be shown again!)
            </li>
          </ol>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="$emit('close')">Close</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script setup>
  defineProps(['value'])
  defineEmits(['close', 'update:value'])
  </script>