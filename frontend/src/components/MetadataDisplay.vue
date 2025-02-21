<template>
  <div class="metadata-container">
    <div class="button-container">
      <button @click="goBack" class="button">Back</button>
      <h2 class="header">Schema: {{ schema }}</h2>
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
          Profile: Software Application
        </button>
      </div>
      <div class="tab-content">
        <MetadataTable
          v-if="activeTab === 'ssc_tab'"
          :data="filterMetadata(results['maSMP:SoftwareSourceCode'])"
          :schema="schema"
          :active-tab="activeTab"
        />
        <MetadataTable
          v-if="activeTab === 'sa_tab'"
          :data="filterMetadata(results['maSMP:SoftwareApplication'])"
          :schema="schema"
          :active-tab="activeTab"
        />
      </div>
    </div>

    <div v-else-if="schema === 'CODEMETA'" class="metadata-content">
      <MetadataTable :data="filterMetadata(results)" :schema="schema"/>
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
  /* General Styles */
  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background-color: #f4f7fb; /* Soft background for the page */
    color: #333;
  }

  .header {
    font-size: 25px;
    color: #42b983;
    text-shadow: -1px -1px 1px rgba(0, 0, 0, 0.6); /* Subtle, smooth text shadow */

  }

  .metadata-container {
    display: flex;
    flex-direction: column;
    padding: 20px;
    max-width: 1200px; /* Increased width */
    margin: 0 auto;
    border: 1px solid #e1e4e8; /* Light border for a subtle look */
    border-radius: 10px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Soft shadow for depth */
    background-color: #e2ede8;
  }

  .tabs-container {
    margin-top: 20px;
  }

  .tabs {
    display: flex;
    gap: 20px;
    border-bottom: 2px solid #e1e4e8; /* Subtle separator */
    padding-bottom: 8px; /* Padding for spacing */
  }

  .tabs button {
    padding: 12px 20px;
    border: none;
    border-radius: 5px;
    background-color: transparent;
    color: #42b983; /* Active tab color */
    border-bottom: 4px solid #42b983; /* Active tab bottom border for emphasis */
    border-right: 4px solid #42b983;
    border-top: 1px solid #42b983;
    border-left: 1px solid #42b983;
    font-size: 16px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    position: relative;
    text-align: center;
  }

  .tabs button.active {
    color: #ffffff; /* Active tab color */
    background-color: #42b983;
    border-bottom: 4px solid #059453;/* Active tab bottom border for emphasis */
    border-right: 4px solid #059453;
    border-top: 1px solid #059453;
    border-left: 1px solid #059453;
  }

  .tabs button:focus {
    outline: none;
  }

  .tab-content {
    background: #f8f8f8;
    padding: 10px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Light shadow for depth */
    margin-top: 20px;
    transition: all 2s ease;
  }

  /* Mobile Responsiveness */
  @media (max-width: 768px) {
    .metadata-container {
      padding: 15px;
      max-width: 100%;
    }

    .tabs {
      flex-direction: column;
      gap: 10px;
      padding-bottom: 0;
    }

    .tabs button {
      width: 100%;
      padding: 14px;
      text-align: left; /* Align text to the left for better readability */
    }

    .tab-content {
      padding: 15px;
    }
  }

  /* Button Styles for Back and Download */
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
    background-color: #42b983; /* Main color for buttons */
    color: white;
    transition: background-color 0.3s ease;
  }

  .button:hover {
    background-color: #36976f; /* Darker shade for hover */
  }

  .metadata-content {
    background: #ffffff;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); /* Light shadow for depth */
  }

</style>