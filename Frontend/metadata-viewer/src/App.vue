<template>
  <div id="app">
    <HomePage v-if="!metadata" @metadata-extracted="handleMetadata" />
    <MetadataDisplay v-else :metadata="metadata" :schema="schema" @go-back="goBack" />
  </div>
</template>

<script>
import HomePage from './components/HomePage.vue';
import MetadataDisplay from './components/MetadataDisplay.vue';

export default {
  components: {
    HomePage,
    MetadataDisplay,
  },
  data() {
    return {
      metadata: null,
      schema: '',
    };
  },
  methods: {
    handleMetadata({ metadata, schema }) {
      this.metadata = metadata;
      this.schema = schema;
    },
    goBack() {
      this.metadata = null;
    },
  },
};
</script>

<style>
#app {
  font-family: Arial, sans-serif;
  text-align: center;
  margin-top: 20px;
}
</style>