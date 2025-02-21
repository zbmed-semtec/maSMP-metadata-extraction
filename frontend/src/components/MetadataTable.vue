<template>
  <table class="metadata-table">
    <tbody>
      <template v-if="schema === 'maSMP'">
        <!-- Apply categorization only for the outer table (depth === 0) -->
        <template v-if="depth === 0">
          <template v-for="category in sortedProperties" :key="category.title">
            <tr>
              <td colspan="2" 
                  class="category-header" 
                  :class="{
                    'required-bg': category.title === 'Required Properties',
                    'recommended-bg': category.title === 'Recommended Properties',
                    'optional-bg': category.title === 'Optional Properties'
                  }">
                {{ category.title }}
              </td>
            </tr>
            <tr v-for="(value, key) in category.properties" :key="key">
              <td class="property">
                <!-- Render property name as a clickable link -->
                <a :href="generatePropertyLink(key)" target="_blank" rel="noopener noreferrer">
                  {{ key }} <span class="link-icon">🔗</span>
                </a>
              </td>
              <td class="value">
                <!-- Render Nested Objects as Inner Tables -->
                <template v-if="isObject(value) && !isSpecialType(value)">
                  <MetadataTable :data="value" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
                </template>

                <!-- Render Special Types (Person, Article, VersionControlSystem) -->
                <template v-else-if="isSpecialType(value)">
                  <span v-html="renderSpecialType(value)" />
                  <template v-if="specialType(value) === 'Article' || specialType(value) === 'VCS'">
                    <MetadataTable v-if="hasAdditionalInfo(value)" :data="filterAdditionalInfo(value)" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
                  </template>
                </template>

                <!-- Render Arrays -->
                <template v-else-if="isArray(value)">
                  <div v-for="(item, index) in value" :key="index" class="array-item">
                    <!-- If item is a special type -->
                    <template v-if="isSpecialType(item)">
                      <span v-html="renderSpecialType(item)" />
                      <template v-if="specialType(item) === 'Article' || specialType(item) === 'VCS'">
                        <MetadataTable v-if="hasAdditionalInfo(item)" :data="filterAdditionalInfo(item)" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
                      </template>
                    </template>

                    <!-- If item is an object but not a special type -->
                    <MetadataTable v-else-if="isObject(item)" :data="item" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>

                    <!-- If item is a primitive -->
                    <span v-else v-html="renderValue(item)" />
                  </div>
                </template>

                <!-- Render Primitive Values (strings, numbers, etc.) -->
                <template v-else>
                  <span v-html="renderValue(value)" />
                </template>
              </td>
            </tr>
          </template>
        </template>

        <!-- For nested tables (depth > 0), render without categorization -->
        <template v-else>
          <tr v-for="(value, key) in data" :key="key">
            <td class="property">{{ key }}</td>
            <td class="value">
              <!-- Render Nested Objects as Inner Tables -->
              <template v-if="isObject(value) && !isSpecialType(value)">
                <MetadataTable :data="value" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
              </template>

              <!-- Render Special Types (Person, Article, VersionControlSystem) -->
              <template v-else-if="isSpecialType(value)">
                <span v-html="renderSpecialType(value)" />
                <template v-if="specialType(value) === 'Article' || specialType(value) === 'VCS'">
                  <MetadataTable v-if="hasAdditionalInfo(value)" :data="filterAdditionalInfo(value)" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
                </template>
              </template>

              <!-- Render Arrays -->
              <template v-else-if="isArray(value)">
                <div v-for="(item, index) in value" :key="index" class="array-item">
                  <!-- If item is a special type -->
                  <template v-if="isSpecialType(item)">
                    <span v-html="renderSpecialType(item)" />
                    <template v-if="specialType(item) === 'Article' || specialType(item) === 'VCS'">
                      <MetadataTable v-if="hasAdditionalInfo(item)" :data="filterAdditionalInfo(item)" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
                    </template>
                  </template>

                  <!-- If item is an object but not a special type -->
                  <MetadataTable v-else-if="isObject(item)" :data="item" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>

                  <!-- If item is a primitive -->
                  <span v-else v-html="renderValue(item)" />
                </div>
              </template>

              <!-- Render Primitive Values (strings, numbers, etc.) -->
              <template v-else>
                <span v-html="renderValue(value)" />
              </template>
            </td>
          </tr>
        </template>
      </template>

      <!-- For CODEMETA schema, render without categorization -->
      <template v-if="schema === 'CODEMETA'">
        <tr v-for="(value, key) in data" :key="key">
          <td class="property">
            <!-- Render property name as a clickable link -->
            <a :href="generatePropertyLink(key)" target="_blank" rel="noopener noreferrer">
              {{ key }} <span class="link-icon">🔗</span>
            </a>
          </td>
          <td class="value">
            <!-- Render Nested Objects as Inner Tables -->
            <template v-if="isObject(value) && !isSpecialType(value)">
              <MetadataTable :data="value" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
            </template>

            <!-- Render Special Types (Person, Article, VersionControlSystem) -->
            <template v-else-if="isSpecialType(value)">
              <span v-html="renderSpecialType(value)" />
              <template v-if="specialType(value) === 'Article' || specialType(value) === 'VCS'">
                <MetadataTable v-if="hasAdditionalInfo(value)" :data="filterAdditionalInfo(value)" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
              </template>
            </template>

            <!-- Render Arrays -->
            <template v-else-if="isArray(value)">
              <div v-for="(item, index) in value" :key="index" class="array-item">
                <!-- If item is a special type -->
                <template v-if="isSpecialType(item)">
                  <span v-html="renderSpecialType(item)" />
                  <template v-if="specialType(item) === 'Article' || specialType(item) === 'VCS'">
                    <MetadataTable v-if="hasAdditionalInfo(item)" :data="filterAdditionalInfo(item)" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>
                  </template>
                </template>

                <!-- If item is an object but not a special type -->
                <MetadataTable v-else-if="isObject(item)" :data="item" :schema="schema" :depth="depth + 1" :active-tab="activeTab"/>

                <!-- If item is a primitive -->
                <span v-else v-html="renderValue(item)" />
              </div>
            </template>

            <!-- Render Primitive Values (strings, numbers, etc.) -->
            <template v-else>
              <span v-html="renderValue(value)" />
            </template>
          </td>
        </tr>
      </template>
    </tbody>
  </table>
</template>

<script>
export default {
  name: 'MetadataTable',
  props: {
    data: {
      type: Object,
      required: true,
    },
    schema: {
      type: String,
      required: true,
    },
    depth: {
      type: Number,
      default: 0, // Default depth is 0 (outer table)
    },
    activeTab: {
      type: String, // 'ssc_tab' or 'sa_tab'
      required: true,
    }
  },
  computed: {
    sortedProperties() {
      // Only apply categorization for the outer table (depth === 0)
      if (this.depth !== 0) {
        return null;
      }

      const propertyLists = {
        'maSMP:SoftwareSourceCode': {
          required: ["name", "description", "url", "codeRepository", "version", "programmingLanguage"],
          recommended: ["author", "citation", "license", "identifier", "keywords", "codemeta:readme", "maSMP:versionControlSystem", "maSMP:intendedUse", "targetProduct", "archivedAt"]
        },
        'maSMP:SoftwareApplication': {
          required: ["name", "description", "url"],
          recommended: ["author", "citation", "license", "identifier", "keywords", "releaseNotes", "codemeta:readme", "archivedAt", "maSMP:intendedUse", "softwareVersion"]
        }
      };

      // Determine which property list to use based on @type
      const type = this.data['@type'] || 'maSMP:SoftwareSourceCode'; // Default to SoftwareSourceCode
      const properties = propertyLists[type] || propertyLists['maSMP:SoftwareSourceCode'];

      const requiredProps = {};
      const recommendedProps = {};
      const optionalProps = {};

      Object.keys(this.data).forEach(key => {
        if (properties.required.includes(key)) {
          requiredProps[key] = this.data[key];
        } else if (properties.recommended.includes(key)) {
          recommendedProps[key] = this.data[key];
        } else {
          optionalProps[key] = this.data[key];
        }
      });

      return [
        { title: 'Required Properties', properties: requiredProps },
        { title: 'Recommended Properties', properties: recommendedProps },
        { title: 'Optional Properties', properties: optionalProps }
      ];
    }
  },
  methods: {
    // Generate dynamic link for property names
    generatePropertyLink(propertyName) {
      if (propertyName.startsWith('codemeta:')) {
        return `https://codemeta.github.io/terms/`;
      } else if (propertyName.startsWith('maSMP:')) {
        if (this.activeTab === 'ssc_tab') {
          return 'https://discovery.biothings.io/ns/maSMPProfiles/maSMPProfiles:SoftwareSourceCodeProfile';
        } else if (this.activeTab === 'sa_tab') {
          return 'https://discovery.biothings.io/ns/maSMPProfiles/maSMPProfiles:SoftwareApplicationProfile';
        }
      } else {
        return `https://schema.org/${propertyName}`;
      }
    },
    // Type Checkers
    isObject(value) {
      return typeof value === 'object' && value !== null && !Array.isArray(value);
    },
    isArray(value) {
      return Array.isArray(value);
    },
    isSpecialType(value) {
      return (
        this.isPerson(value) ||
        this.isArticle(value) ||
        this.isVersionControlSystem(value)
      );
    },
    specialType(value){
       if (this.isPerson(value)){
        return "Person";
       } else if (this.isArticle(value)){
        return "Article";
       } else if (this.isVersionControlSystem(value)){
        return "VCS";
       }
    },
    isPerson(value) {
      return value !== null && this.isObject(value) && value['@type']?.trim() === 'Person';
    },

    isArticle(value) {
      return value !== null && this.isObject(value) && ['Article', 'ScholarlyArticle'].includes(value['@type']?.trim());
    },
    isVersionControlSystem(value) {
      return this.isObject(value) && value['@type'] === 'SoftwareApplication' && value['@id'] && value['url'] && value['name'];
    },

    // Render Methods
    renderSpecialType(value) {
      if (this.isPerson(value)) {
        return this.renderPerson(value);
      } else if (this.isArticle(value)) {
        return this.renderArticle(value);
      } else if (this.isVersionControlSystem(value)) {
        return this.renderVersionControlSystem(value);
      }
      return '';
    },
    renderPerson(person) {
      if (person.url) {
        return `👤<a href="${person.url}" target="_blank" rel="noopener noreferrer">${person.url}</a>`;
      } else {
        const givenName = person.givenName || '';
        const familyName = person.familyName || '';
        const orcid = person['@id'] ? ` : <a href="${person['@id']}" target="_blank" rel="noopener noreferrer">${person['@id']}</a>` : '';
        return `👤${givenName} ${familyName}${orcid}`;
      }
    },
    renderArticle(article) {
      return `📝: <a href="${article['@id']}" target="_blank" rel="noopener noreferrer">${article['@id']}</a>`;
    },
    renderVersionControlSystem(vcs) {
      return `SoftwareApplication: <a href="${vcs['@id']}" target="_blank" rel="noopener noreferrer">${vcs['@id']}</a>`;
    },
    renderValue(value) {
      if (value === null) {
        return `<span style="color: red; font-style: italic;">Details are missing. Please consider updating the repository.</span>`;
      }
      if (typeof value === 'string' && this.isUrl(value)) {
        return `<a href="${value}" target="_blank" rel="noopener noreferrer">${value}</a>`;
      }
      return value;
    },
    isUrl(value) {
      return /^(https?:\/\/)?([\w.-]+)\.([a-z]{2,})(\/\S*)?$/i.test(value);
    },

    // Helper Methods
    hasAdditionalInfo(obj) {
      // eslint-disable-next-line no-unused-vars
      const { '@type': type, '@id': id, ...rest } = obj;
      return Object.keys(rest).length > 0;
    },
    filterAdditionalInfo(obj) {
      // eslint-disable-next-line no-unused-vars
      const { '@type': type, '@id': id, ...rest } = obj;
      return rest;
    },
  },
};
</script>

<style scoped>
.metadata-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0 10px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f8f8;
}

.metadata-table td {
  padding: 20px;
  text-align: left;
  background-color: #ffffff;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  border-radius: 8px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.metadata-table .property {
  font-weight: bold;
  font-size: 40px;
  color:  #42b983;
  background-color: #ffffff;
  border: 5x solid #059453;
  width: 30%;
  padding-right: 15px;
  border-radius: 8px 0 0 8px;
}

.metadata-table .value {
  background-color: #ffffff;
  color: #555;
  border-radius: 0 8px 8px 0;
  
}

.metadata-table tr:last-child td {
  border-bottom: none;
}

.metadata-table tr:hover td {
  transform: translateY(-2px);
  box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
}

.metadata-table .array-item {
  margin-bottom: 10px;
  padding-left: 20px;
}

.metadata-table .array-item:last-child {
  margin-bottom: 0;
}

a {
  color: #059453;
  text-decoration: none;
  font-weight: 500;
  border-bottom: 1px solid transparent;
  transition: border-color 0.3s ease;
}

a:hover {
  text-decoration: none;
  border-bottom: 1px solid #059453;
}

.metadata-table .property,
.metadata-table .value {
  font-size: 16px;
  line-height: 1.6;
}

.metadata-table .value {
  font-size: 14px;
  color: #666;
}

.metadata-table .value span {
  display: inline-block;
  margin-bottom: 10px;
}

.metadata-table .value a {
  display: inline-block;
  color: #059453;
}

.metadata-table .value a:hover {
  text-decoration: underline;
}

.metadata-table .array-item {
  font-size: 14px;
  color: #666;
  margin-bottom: 12px;
  padding-left: 10px;
}

.metadata-table .array-item:last-child {
  margin-bottom: 0;
}

.metadata-table tr td {
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  color: #4d4d4d;
}

.metadata-table .metadata-table {
  margin-top: 20px;
}

.metadata-table .metadata-table tr:hover {
  background-color: #f1f1f1;
}

@media (max-width: 768px) {
  .metadata-table {
    font-size: 14px;
  }

  .metadata-table .property {
    font-size: 13px;
  }

  .metadata-table .value {
    font-size: 12px;
  }

  .metadata-table .array-item {
    font-size: 12px;
  }
}

.metadata-table .category-header.required-bg {
  color: red;
  font-size: 20px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 1);
  text-align: center;
  background-color: rgb(248, 222, 222);
}

.metadata-table .category-header.recommended-bg {
  color: rgb(251, 222, 5);
  font-size: 20px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 1);
  text-align: center;
  background-color: rgb(245, 245, 225);

}

.metadata-table .category-header.optional-bg {
  color: green;
  font-size: 20px;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 1);
  text-align: center;
  background-color: #e2ede8;
}

.link-icon {
  font-size: 0.8em;
  margin-left: 5px;
}
</style>