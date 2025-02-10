<template>
  <div id="app">
    <component 
      :is="currentComponent"
      :metadata="metadata"
      @metadata-extracted="handleMetadata"
      @back="showHome"
    />
  </div>
</template>

<script>
import HomePage from './components/HomePage.vue';
import MetadataDisplay from './components/MetadataDisplay.vue';

export default {
  components: {
    HomePage,
    MetadataDisplay
  },
  data() {
    return {
      metadata: null,
      currentComponent: 'HomePage'
    };
  },
  methods: {
    handleMetadata(metadata) {
      this.metadata = metadata;
      this.currentComponent = 'MetadataDisplay';
    },
    showHome() {
      this.currentComponent = 'HomePage';
      this.metadata = null;
    }
  }
};
</script>

<style>
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css');

#app {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin: 0;
  padding: 20px;
}

* {
  box-sizing: border-box;
}

button {
  font-family: inherit;
}
</style>