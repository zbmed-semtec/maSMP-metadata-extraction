<template>
  <div>
    <LoadingScreen v-if="isLoading" />
    <MetadataForm
      :githubUrl="githubUrl"
      :accessCode="accessCode"
      :selectedSchema="selectedSchema"
      :schemas="schemas"
      :githubUrlError="githubUrlError"
      :schemaError="schemaError"
      @update:githubUrl="githubUrl = $event"
      @update:accessCode="accessCode = $event"
      @update:selectedSchema="selectedSchema = $event"
      @validateAndExtract="validateAndExtract"
      @showAccessTokenInfo="showAccessTokenInfo = true"
    />
    <MASMPResultsContainer
      v-if="filteredResults && responseSchema === 'maSMP'"
      :results="filteredResults"
      :activeTab="activeTab"
      :categories="categories"
      @update:activeTab="activeTab = $event"
      @downloadJson="downloadJson"
      :getProperties="getProperties"
      :formatValue="formatValue"
    />
    <CODEMETAResultsContainer
      v-if="filteredResults && responseSchema === 'CODEMETA'"
      :results="filteredResults"
      :activeTab="activeTab"
      @update:activeTab="activeTab = $event"
      @downloadJson="downloadJson"
      :getPropertiesWithoutCategories="getPropertiesWithoutCategories"
      :formatValue="formatValue"
    />
    <InfoDialog
      v-model="showAccessTokenInfo"
      @close="showAccessTokenInfo = false"
    />
    <ErrorSnackbar
      v-model="showError"
      :errorMessage="errorMessage"
      @close="showError = false"
    />
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import MetadataForm from '/components/MetadataForm.vue'
import InfoDialog from '/components/InfoDialog.vue'
import ErrorSnackbar from '/components/ErrorSnackbar.vue'
import LoadingScreen from '/components/LoadingScreen.vue'
import MASMPResultsContainer from '/components/MASMPResultsContainer.vue'
import CODEMETAResultsContainer from '/components/CODEMETAResultsContainer.vue'

const githubUrl = ref('')
const accessCode = ref('')
const selectedSchema = ref(null)
const schemas = ref(['maSMP', 'CODEMETA'])
const showAccessTokenInfo = ref(false)
const results = ref(null)
const filteredResults = ref(null)
const activeTab = ref('sourceCode')
const categories = ref(['Required', 'Recommended', 'Optional'])
const githubUrlError = ref('')
const schemaError = ref('')
const showError = ref(false)
const errorMessage = ref('')
const isLoading = ref(false)
const responseSchema = ref(null)

const propertyLists = {
  'maSMP:SoftwareSourceCode': {
    required: ['name', 'description', 'url', 'codeRepository', 'version', 'programmingLanguage'],
    recommended: ['author', 'citation', 'license', 'identifier', 'keywords', 'codemeta:readme', 'maSMP:versionControlSystem', 'maSMP:intendedUse', 'targetProduct', 'archivedAt'],
  },
  'maSMP:SoftwareApplication': {
    required: ['name', 'description', 'url'],
    recommended: ['author', 'citation', 'license', 'identifier', 'keywords', 'releaseNotes', 'codemeta:readme', 'archivedAt', 'maSMP:intendedUse', 'softwareVersion'],
  },
}

const validateAndExtract = () => {
  githubUrlError.value = ''
  schemaError.value = ''
  let isValid = true

  if (!githubUrl.value) {
    githubUrlError.value = 'GitHub URL is required'
    isValid = false
  }
  if (!selectedSchema.value) {
    schemaError.value = 'Schema selection is required'
    isValid = false
  }

  if (!isValid) {
    errorMessage.value = 'Please fill in all required fields'
    showError.value = true
    return
  }

  extractData()
}

const extractData = async () => {
  isLoading.value = true
  try {
    const params = new URLSearchParams({
      repo_url: githubUrl.value ?? githubUrl,
      schema: selectedSchema.value,
      access_token: accessCode.value ?? accessCode
    });
    const newResponse = await fetch(`http://localhost:8000/metadata?${params.toString()}`, {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    });

    const data = await newResponse.json();
    results.value = data.results
    responseSchema.value = data.schema
    console.log(selectedSchema.value)
    console.log(data)
  } catch (error) {
    console.log(error)
    errorMessage.value = 'Error fetching data'
    showError.value = true
  } finally {
    isLoading.value = false
  }
}

const filterMetadata = (data) => {
  if (!data) return null
  const filtered = { ...data }
  if (filtered['maSMP:SoftwareSourceCode']) {
    filtered['maSMP:SoftwareSourceCode'] = { ...filtered['maSMP:SoftwareSourceCode'] }
    delete filtered['maSMP:SoftwareSourceCode']['@context']
    delete filtered['maSMP:SoftwareSourceCode']['@type']
  }
  if (filtered['maSMP:SoftwareApplication']) {
    filtered['maSMP:SoftwareApplication'] = { ...filtered['maSMP:SoftwareApplication'] }
    delete filtered['maSMP:SoftwareApplication']['@context']
    delete filtered['maSMP:SoftwareApplication']['@type']
  }
  return filtered
}

watch(results, (newResults) => {
  filteredResults.value = filterMetadata(newResults)
}, { deep: true })

const getProperties = (profile, category) => {
  const selectedProfile = activeTab.value === 'sourceCode' ? 'maSMP:SoftwareSourceCode' : 'maSMP:SoftwareApplication';
  const props = propertyLists[selectedProfile][category.toLowerCase()] || []; 
  const resultProps = filteredResults.value[selectedProfile] || {};
  if (category === 'optional') {
    return Object.keys(resultProps).filter(
      (prop) => !propertyLists[selectedProfile].required.includes(prop) &&
                !propertyLists[selectedProfile].recommended.includes(prop)
    );
  }
  return props.filter((prop) => resultProps[prop] !== null && resultProps[prop] !== undefined);
  
};

const getPropertiesWithoutCategories = () => {
  const properties = Object.keys(filteredResults.value).filter(
    (prop) => filteredResults.value[prop] !== null && 
            filteredResults.value[prop] !== undefined &&
            prop !== '@context' &&
            prop !== '@type'
  );
  console.log('CODEMETA Properties:', properties);
  return properties;
};

const formatValue = (value) => {
  if (Array.isArray(value)) {
    if (value[0] && typeof value[0] === 'object') {
      return value.map((item) => {
        if (item['@type'] === 'Person') {
          const name = item.givenName ? `${item.givenName} ${item.familyName || ''}`.trim() : ''
          // Check for ORCID ID first, then fallback to URL
          if (item['@id'] && item['@id'].includes('orcid.org')) {
            return `<a href="${item['@id']}" target="_blank" class="fancy-link">${name || item['@id']}</a>`
          }
          return name || item['@id'] || item.url || 'N/A'
        }
        return item.name || item['@id'] || JSON.stringify(item)
      }).join(', ')
    }
    return value.join(', ')
  }
  if (typeof value === 'object' && value !== null) {
    if (value['@type'] === 'Person') {
      const name = `${value.givenName || ''} ${value.familyName || ''}`.trim()
      // Check for ORCID ID first, then fallback to URL
      if (value['@id'] && value['@id'].includes('orcid.org')) {
        return `<a href="${value['@id']}" target="_blank" class="fancy-link">${name || value['@id']}</a>`
      }
      return name || value['@id'] || value.url || 'N/A'
    }
    if (value.name) return value.name
    if (value['@id']) return value['@id']
    return JSON.stringify(value)
  }
  return value || 'N/A'
}

const downloadJson = () => {
  let dataToDownload = null
  let fileName = ''

  if (selectedSchema.value === 'CODEMETA') {
    dataToDownload = results.value
    fileName = 'codemeta_data.json'
  } else if (selectedSchema.value === 'maSMP') {
    if (activeTab.value === 'sourceCode') {
      dataToDownload = results.value['maSMP:SoftwareSourceCode']
      fileName = 'maSMP_SoftwareSourceCode.json'
    } else if (activeTab.value === 'application') {
      dataToDownload = results.value['maSMP:SoftwareApplication']
      fileName = 'maSMP_SoftwareApplication.json'
    }
  }

  if (!dataToDownload) return

  const cleanedData = Object.fromEntries(
    Object.entries(dataToDownload).filter(([_, value]) => value !== null)
  )

  const jsonString = JSON.stringify(cleanedData, null, 2)
  const blob = new Blob([jsonString], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.fancy-link {
  display: inline-block;
  text-decoration: none;
  color: #1976d2;
  font-weight: 500;
  transition: all 0.3s ease;
  border-bottom: 1px solid transparent;
}

.fancy-link:hover {
  color: #1565c0;
  border-bottom-color: #1565c0;
  transform: translateY(-1px);
}
</style>