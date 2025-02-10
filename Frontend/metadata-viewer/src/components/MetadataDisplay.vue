<template>
  <div class="metadata-display">
    <div class="header">
      <button @click="goBack" class="back-button">Back</button>
      <button @click="downloadJson" class="download-button">Download JSON</button>
    </div>

    <!-- Display tabs only for maSMP schema -->
    <div v-if="schema === 'maSMP'" class="tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['tab-button', { active: currentTab === tab }]"
        @click="currentTab = tab"
      >
        {{ tab }}
      </button>
    </div>

    <!-- Tab content displayed based on selected tab -->
    <div v-if="schema === 'maSMP'" class="tab-content">
      <!-- Tab 1: SoftwareSourceCode -->
      <div v-if="currentTab === 'maSMP:SoftwareSourceCode'">
        <MetadataTable :metadata="metadata.results['maSMP:SoftwareSourceCode']" :schema="schema" />
      </div>

      <!-- Tab 2: SoftwareApplication -->
      <div v-if="currentTab === 'maSMP:SoftwareApplication'">
        <MetadataTable :metadata="metadata.results['maSMP:SoftwareApplication']" :schema="schema" />
      </div>
    </div>

    <!-- For other schemas like CodeMeta, display properties directly in a nested table -->
    <div v-else>
      <MetadataTable :metadata="metadata" :schema="schema" />
    </div>
  </div>
</template>

<script>
import MetadataTable from './MetadataTable.vue';

export default {
  components: {
    MetadataTable,
  },
  props: {
    metadata: {
      type: Object,
      required: true,
    },
    schema: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      currentTab: 'maSMP:SoftwareSourceCode', // Default tab
      tabs: ['maSMP:SoftwareSourceCode', 'maSMP:SoftwareApplication'],
    };
  },
  methods: {
    goBack() {
      this.$emit('go-back');
    },
    downloadJson() {
      const dataStr = JSON.stringify(this.metadata, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = 'metadata.json';
      link.click();
      URL.revokeObjectURL(url);
    },
  },
};
</script>

<style scoped>
.metadata-display {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.back-button, .download-button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
  border-radius: 5px;
}

.tabs {
  display: flex;
  margin-bottom: 20px;
}

.tab-button {
  padding: 10px 20px;
  background-color: #f4f4f4;
  border: none;
  cursor: pointer;
  margin-right: 10px;
  border-radius: 5px;
}

.tab-button.active {
  background-color: #42b983;
  color: white;
}

.tab-content {
  background-color: #f9f9f9;
  padding: 20px;
  border-radius: 5px;
}
</style>
