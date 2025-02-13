<template>
  <div>
    <!-- Render Person -->
    <template v-if="isPerson(value)">
      <span v-html="renderPerson(value)" />
    </template>

    <!-- Render Article or ScholarlyArticle -->
    <template v-else-if="isArticle(value)">
      <span v-html="renderArticle(value)" />
      <MetadataTable v-if="hasAdditionalInfo(value)" :data="filterArticleInfo(value)" />
    </template>

    <!-- Render VersionControlSystem -->
    <template v-else-if="isVersionControlSystem(value)">
      <span v-html="renderVersionControlSystem(value)" />
      <MetadataTable v-if="hasAdditionalInfo(value)" :data="filterVersionControlSystemInfo(value)" />
    </template>

    <!-- Render Nested Objects -->
    <template v-else-if="isObject(value)">
      <MetadataTable :data="value" />
    </template>

    <!-- Render Arrays -->
    <template v-else-if="isArray(value)">
      <div v-for="(item, index) in value" :key="index" class="array-item">
        <ValueRenderer :value="item" />
      </div>
    </template>

    <!-- Render Primitive Values (strings, numbers, etc.) -->
    <template v-else>
      <span v-html="renderValue(value)" />
    </template>
  </div>
</template>

<script>
import MetadataTable from './MetadataTable.vue';

export default {
  name: 'ValueRenderer',
  components: {
    MetadataTable,
  },
  props: {
    value: {
      type: [Object, Array, String, Number, Boolean],
      required: true,
    },
  },
  methods: {
    // Type Checkers
    isObject(value) {
      return typeof value === 'object' && value !== null && !Array.isArray(value);
    },
    isArray(value) {
      return Array.isArray(value);
    },
    isPerson(value) {
      return this.isObject(value) && value['@type'] === 'Person';
    },
    isArticle(value) {
      return this.isObject(value) && (value['@type'] === 'Article' || value['@type'] === 'ScholarlyArticle');
    },
    isVersionControlSystem(value) {
      return this.isObject(value) && value['@type'] === 'SoftwareApplication' && value['@id'] && value['url'] && value['name'];
    },

    // Render Methods
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
    filterArticleInfo(article) {
      // eslint-disable-next-line no-unused-vars
      const { '@type': type, '@id': id, ...rest } = article;
      return rest;
    },
    filterVersionControlSystemInfo(vcs) {
      // eslint-disable-next-line no-unused-vars
      const { '@type': type, '@id': id, ...rest } = vcs;
      return rest;
    },
  },
};
</script>

<style scoped>
.array-item {
  margin-bottom: 8px;
}

.array-item:last-child {
  margin-bottom: 0;
}

a {
  color: #007bff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>