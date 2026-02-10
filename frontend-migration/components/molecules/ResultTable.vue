<template>
  <div class="overflow-hidden rounded-lg border border-gray-200 bg-white">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 text-left text-sm">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-4 py-3 font-medium text-gray-700">
              Property
            </th>
            <th scope="col" class="px-4 py-3 font-medium text-gray-700">
              Value
            </th>
            <th v-if="showSource" scope="col" class="px-4 py-3 font-medium text-gray-700">
              Source
            </th>
            <th v-if="showConfidence" scope="col" class="px-4 py-3 font-medium text-gray-700">
              Confidence
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200 bg-white">
          <tr
            v-for="(row, i) in rows"
            :key="i"
            class="hover:bg-gray-50/80"
          >
            <td class="px-4 py-3 font-medium text-secondary-800">
              {{ row.property }}
            </td>
            <td class="max-w-md px-4 py-3 text-gray-700 break-words">
              {{ row.value }}
            </td>
            <td v-if="showSource" class="px-4 py-3">
              <span
                class="inline-flex items-center rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-700"
              >
                {{ row.source }}
              </span>
            </td>
            <td v-if="showConfidence" class="px-4 py-3">
              <span
                class="inline-flex items-center rounded-md bg-primary-50 px-2 py-0.5 text-xs font-medium text-primary-700"
              >
                {{ row.confidence }}
              </span>
            </td>
          </tr>
          <tr v-if="!rows.length">
            <td :colspan="showSource && showConfidence ? 4 : 2" class="px-4 py-6 text-center text-gray-500">
              No properties in this section.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    rows: { property: string; value: string; source: string; confidence: string }[]
    showSource: boolean
    showConfidence: boolean
  }>(),
  { showSource: true, showConfidence: true }
)
</script>
