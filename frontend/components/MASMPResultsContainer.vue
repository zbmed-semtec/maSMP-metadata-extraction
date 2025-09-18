<template>
  <v-container class="mt-6">
    <v-row align="center">
      <v-col cols="12" md="6">
        <v-tabs :value="activeTab" color="primary" @update:modelValue="$emit('update:activeTab', $event)">
          <v-tab value="sourceCode">Software Source Code</v-tab>
          <v-tab value="application">Software Application</v-tab>
        </v-tabs>
      </v-col>
      <v-col cols="12" md="6" class="d-flex justify-end">
        <v-btn color="#000055" rounded="l" @click="$emit('downloadJson')">
          <v-icon start>mdi-download</v-icon>
          Download JSON
        </v-btn>
      </v-col>
    </v-row>
    <v-window :value="activeTab">
      <v-window-item value="sourceCode">
        <v-expansion-panels class="mt-4">
          <v-expansion-panel v-for="category in categories" :key="category">
            <v-expansion-panel-title :class="getCategoryClass(category)">
              <v-icon start :icon="getCategoryIcon(category)" class="mr-2"></v-icon>
              {{ category }}
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <v-table class="expandable-table">
                <tbody>
                  <tr
                    v-for="prop in getProperties('maSMP:SoftwareSourceCode', category.toLowerCase())"
                    :key="prop"
                  >
                    <td class="prop-cell">
                      <strong>{{ prop }}</strong>
                      <a
                        :href="getPropertyLink(prop, 'sourceCode')"
                        target="_blank"
                        class="property-link"
                      >
                        <v-icon small class="ml-1">mdi-open-in-new</v-icon>
                      </a>
                    </td>
                    <td class="value-cell">
                      <span v-if="isMissingValue(results['maSMP:SoftwareSourceCode'][prop])" class="missing-value">
                        {{ resolveValue(formatValue(results['maSMP:SoftwareSourceCode'][prop])) }}
                      </span>
                      <span v-else v-html="formatValueWithLinks(results['maSMP:SoftwareSourceCode'][prop])"></span>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-window-item>
      <v-window-item value="application">
        <v-expansion-panels class="mt-4">
          <v-expansion-panel v-for="category in categories" :key="category">
            <v-expansion-panel-title :class="getCategoryClass(category)">
              <v-icon start :icon="getCategoryIcon(category)" class="mr-2"></v-icon>
              {{ category }}
            </v-expansion-panel-title>
            <v-expansion-panel-text>
              <v-table class="expandable-table">
                <tbody>
                  <tr
                    v-for="prop in getProperties('maSMP:SoftwareApplication', category.toLowerCase())"
                    :key="prop"
                  >
                    <td class="prop-cell">
                      <strong>{{ prop }}</strong>
                      <a
                        :href="getPropertyLink(prop, 'application')"
                        target="_blank"
                        class="property-link"
                      >
                        <v-icon small class="ml-1">mdi-open-in-new</v-icon>
                      </a>
                    </td>
                    <td class="value-cell">
                      <span v-if="isMissingValue(results['maSMP:SoftwareApplication'][prop])" class="missing-value">
                        {{ resolveValue(formatValue(results['maSMP:SoftwareApplication'][prop])) }}
                      </span>
                      <span v-else v-html="formatValueWithLinks(results['maSMP:SoftwareApplication'][prop])"></span>
                    </td>
                  </tr>
                </tbody>
              </v-table>
            </v-expansion-panel-text>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-window-item>
    </v-window>
  </v-container>
</template>

<script setup>
defineProps(['results', 'activeTab', 'categories', 'getProperties', 'formatValue'])
defineEmits(['update:activeTab', 'downloadJson'])

const getCategoryClass = (category) => {
  switch (category) {
    case 'Required':
      return 'required-category'
    case 'Recommended':
      return 'recommended-category'
    case 'Optional':
      return 'optional-category'
    default:
      return ''
  }
}

const getCategoryIcon = (category) => {
  switch (category) {
    case 'Required':
      return 'mdi-alert-circle'
    case 'Recommended':
      return 'mdi-check-circle'
    case 'Optional':
      return 'mdi-information-outline'
    default:
      return ''
  }
}

const getPropertyLink = (prop, tab) => {
  if (prop.startsWith('codemeta:')) {
    return 'https://codemeta.github.io/terms/'
  } else if (prop.startsWith('maSMP:')) {
    return tab === 'sourceCode'
      ? 'https://discovery.biothings.io/ns/maSMPProfiles/maSMPProfiles:SoftwareSourceCodeProfile'
      : 'https://discovery.biothings.io/ns/maSMPProfiles/maSMPProfiles:SoftwareApplicationProfile'
  }
  return `https://schema.org/${prop}`
}

const isMissingValue = (value) => {
  return value === null || value === 'N/A' || value === undefined
}

const resolveValue = (value) => {
  if (isMissingValue(value)) {
    return 'Property value not found! Please consider updating your repository'
  }
  return value
}

const isLink = (value) => {
  if (!value || typeof value !== 'string') return false
  return value.startsWith('http://') || value.startsWith('https://')
}

const formatValueWithLinks = (value) => {
  if (isMissingValue(value)) return value
  if (Array.isArray(value)) {
    return value.map(item => {
      if (item && typeof item === 'object') {
        if (item['@type'] === 'Person') {
          const name = item.givenName ? `${item.givenName} ${item.familyName || ''}`.trim() : ''
          // Check for ORCID ID first, then fallback to URL
          if (item['@id'] && item['@id'].includes('orcid.org')) {
            return `<a href="${item['@id']}" target="_blank" class="fancy-link">${name || item['@id']}</a>`
          }
          if (item.url && isLink(item.url)) {
            return `<a href="${item.url}" target="_blank" class="fancy-link">${name || item.url}</a>`
          }
          return name || item['@id'] || item.url || 'N/A'
        }
        if (item['@type'] === 'Article' && item['@id'] && isLink(item['@id'])) {
          return `<a href="${item['@id']}" target="_blank" class="fancy-link">${item['@id']}</a>`
        }
        if (item.url && isLink(item.url)) {
          return `<a href="${item.url}" target="_blank" class="fancy-link">${item.name || item.url}</a>`
        }
        return item.name || item['@id'] || JSON.stringify(item)
      }
      if (isLink(item)) {
        return `<a href="${item}" target="_blank" class="fancy-link">${item}</a>`
      }
      return item
    }).join(', ')
  }
  if (typeof value === 'object' && value !== null) {
    if (value['@type'] === 'Person') {
      const name = `${value.givenName || ''} ${value.familyName || ''}`.trim()
      // Check for ORCID ID first, then fallback to URL
      if (value['@id'] && value['@id'].includes('orcid.org')) {
        return `<a href="${value['@id']}" target="_blank" class="fancy-link">${name || value['@id']}</a>`
      }
      if (value.url && isLink(value.url)) {
        return `<a href="${value.url}" target="_blank" class="fancy-link">${name || value.url}</a>`
      }
      return name || value['@id'] || value.url || 'N/A'
    }
    if (value['@type'] === 'Article' && value['@id'] && isLink(value['@id'])) {
      return `<a href="${value['@id']}" target="_blank" class="fancy-link">${value['@id']}</a>`
    }
    if (value.url && isLink(value.url)) {
      return `<a href="${value.url}" target="_blank" class="fancy-link">${value.name || value.url}</a>`
    }
    if (value.name) return value.name
    if (value['@id']) return value['@id']
    return JSON.stringify(value)
  }
  if (isLink(value)) {
    return `<a href="${value}" target="_blank" class="fancy-link">${value}</a>`
  }
  return value || 'N/A'
}
</script>

<style scoped>
.required-category {
  color: red;
  font-weight: bolder;
}
.recommended-category {
  color: #33a12b;
  font-weight: bolder;
}
.optional-category {
  color: orange;
  font-weight: bolder;
}
.property-link {
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  font-size: xx-small;
}
.expandable-table {
  width: 100%;
  table-layout: auto;
}
.expandable-table tr {
  transition: all 0.3s ease;
}

.expandable-table tr:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  background-color: rgba(191, 165, 246, 0.05);
}
.prop-cell {
  white-space: nowrap;
  padding-right: 16px;
}
.value-cell {
  white-space: normal;
  word-break: break-word;
  min-width: 200px;
}
.missing-value {
  color: red;
}
.fancy-link {
  display: inline-block;
  text-decoration: none;
  color: #1e88e5;
  background: linear-gradient(90deg, #1e88e5, #42a5f5);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  padding: 2px 4px;
  border-radius: 4px;
  transition: all 0.3s ease;
}
.fancy-link:hover {
  transform: translateY(-2px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}
</style>