<template>
  <table class="metadata-table">
    <tbody>
      <!-- Iterate through each property in processedMetadata -->
      <tr v-for="(value, key) in processedMetadata" :key="key">
        <td><strong>{{ key }}</strong></td>
        <td>
          <template v-if="typeof value === 'object' && value !== null">
            <MetadataTable :metadata="value" :schema="schema" />
          </template>
          <template v-else>
            <span v-html="formattedValue(value)"></span>
          </template>
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
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
  computed: {
    // Process metadata to exclude unwanted properties and categorize them based on schema
    processedMetadata() {
      let filteredMetadata = { ...this.metadata };

      // Remove unwanted properties
      const unwantedKeys = ['status', 'schema', 'code_url', 'message'];
      unwantedKeys.forEach((key) => {
        delete filteredMetadata[key];
      });

      // Define the property categorization based on the schema
      const propertyLists = {
        'maSMP:SoftwareSourceCode': {
          required: [
            "name", "description", "url", "codeRepository", "version", "programmingLanguage"
          ],
          recommended: [
            "author", "citation", "license", "identifier", "keywords", "codemeta:readme", 
            "maSMP:versionControlSystem", "maSMP:intendedUse", "targetProduct", "archivedAt"
          ]
        },
        'maSMP:SoftwareApplication': {
          required: [
            "name", "description", "url"
          ],
          recommended: [
            "author", "citation", "license", "identifier", "keywords", "releaseNotes", 
            "codemeta:readme", "archivedAt", "maSMP:intendedUse", "softwareVersion"
          ]
        }
      };

      // Get the required and recommended properties for the current schema
      const schemaProperties = propertyLists[this.schema] || { required: [], recommended: [] };
      const { required, recommended } = schemaProperties;

      // Create an object to categorize properties
      const categorizedMetadata = {
        required: {},
        recommended: {},
        optional: {},
      };

      // Categorize properties
      for (const key in filteredMetadata) {
        if (required.includes(key)) {
          categorizedMetadata.required[key] = filteredMetadata[key];
        } else if (recommended.includes(key)) {
          categorizedMetadata.recommended[key] = filteredMetadata[key];
        } else {
          categorizedMetadata.optional[key] = filteredMetadata[key];
        }
      }

      // Merge required, recommended, and optional properties
      return { ...categorizedMetadata.required, ...categorizedMetadata.recommended, ...categorizedMetadata.optional };
    },
  },
  methods: {
    // Format the value for display
    formattedValue(value) {
      if (value === null) {
        return '<span class="property-missing">Property missing, consider updating the repository</span>';
      }

      if (typeof value === 'string' && (value.startsWith('https://') || value.startsWith('http://'))) {
        return `<a href="${value}" target="_blank">${value}</a>`;
      }

      return value;
    },
  },
};
</script>

<style scoped>
.metadata-table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

.metadata-table th,
.metadata-table td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

.metadata-table th {
  background-color: #f4f4f4;
}

.property-missing {
  color: red;
  font-weight: bold;
}
</style>
