<template>
  <div class="metadata-container">
    <div class="button-container">
      <button @click="goBack" class="button">Back</button>
      <button @click="downloadJson" class="button">Download</button>
    </div>

    <div v-if="schema === 'maSMP'" class="tabs-container">
      <div class="tabs">
        <button
          @click="activeTab = 'ssc_tab'"
          :class="{ active: activeTab === 'ssc_tab' }"
        >
          Profile: Software Source Code
        </button>
        <button
          @click="activeTab = 'sa_tab'"
          :class="{ active: activeTab === 'sa_tab' }"
        >
          Profile: SoftwareApplication
        </button>
      </div>
      <div class="tab-content">
        <MetadataTable
          v-if="activeTab === 'ssc_tab'"
          :data="filterMetadata(results['maSMP:SoftwareSourceCode'])"
        />
        <MetadataTable
          v-if="activeTab === 'sa_tab'"
          :data="filterMetadata(results['maSMP:SoftwareApplication'])"
        />
      </div>
    </div>

    <div v-else-if="schema === 'CODEMETA'" class="metadata-content">
      <MetadataTable :data="filterMetadata(results)" />
    </div>

    <div v-else class="metadata-content">
      <p>No results to display.</p>
    </div>
  </div>
</template>

<script>
import MetadataTable from './MetadataTable.vue'; // Import the MetadataTable component

export default {
  components: {
    MetadataTable,
  },
  data() {
    return {
      metadata: {},
      schema: '',
      results: {},
      activeTab: 'ssc_tab',
    };
  },
  created() {
    const metadataString = this.$route.query.metadata;
    if (metadataString) {
      this.metadata = JSON.parse(metadataString);
      this.schema = this.metadata.schema;
      this.results = this.metadata.results;
    }
  },
  methods: {
    goBack() {
      this.$router.push('/'); // Navigate back to the home page
    },
    downloadJson() {
      let dataToDownload;
      let filename;

      // Helper function to remove null values from an object
      const removeNullValues = (obj) => {
        return Object.fromEntries(
          // eslint-disable-next-line no-unused-vars
          Object.entries(obj).filter(([key, value]) => value !== null)
        );
      };

      if (this.schema === 'CODEMETA') {
        // Download the results directly for CODEMETA schema
        dataToDownload = removeNullValues(this.results);
        filename = 'codemeta_data.json';
      } else if (this.schema === 'maSMP') {
        // Download the active tab's data for maSMP schema
        if (this.activeTab === 'ssc_tab') {
          dataToDownload = removeNullValues(this.results['maSMP:SoftwareSourceCode']);
          filename = 'maSMP_SoftwareSourceCode.json';
        } else if (this.activeTab === 'sa_tab') {
          dataToDownload = removeNullValues(this.results['maSMP:SoftwareApplication']);
          filename = 'maSMP_SoftwareApplication.json';
        }
      } else {
        // Fallback in case of unknown schema
        console.error('Unknown schema:', this.schema);
        return;
      }

      // Convert the data to a JSON string
      const dataStr = JSON.stringify(dataToDownload, null, 2);

      // Create a Blob and trigger the download
      const blob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      link.click();
      URL.revokeObjectURL(url); // Clean up
    },
    filterMetadata(data) {
      // Remove @context and @type from the metadata
      // eslint-disable-next-line no-unused-vars
      const { '@context': context, '@type': type, ...filteredData } = data;
      return filteredData;
    },
  },
};
</script>

<style scoped>
.metadata-container {
  display: flex;
  flex-direction: column;
  padding: 20px;
  max-width: 1200px; /* Increased width */
  margin: 0 auto;
  border: 1px solid #ccc;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  background: #ffffff;
}

.button-container {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
  background-color: #42b983;
  color: white;
  transition: background-color 0.3s ease;
}

.button:hover {
  background-color: #36976f;
}

.tabs-container {
  margin-top: 20px;
}

.tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.tabs button {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  background-color: #f4f4f4;
  color: #333;
  transition: all 0.3s ease;
  font-weight: 500;
}

.tabs button.active {
  background-color: #007bff;
  color: white;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.tab-content {
  background: #f4f4f4;
  padding: 20px;
  border-radius: 5px;
  overflow-x: auto;
}

.metadata-content {
  background: #f4f4f4;
  padding: 20px;
  border-radius: 5px;
  overflow-x: auto;
}
</style>