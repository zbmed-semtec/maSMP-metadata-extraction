<template>
  <div class="home">
    <h1>Metadata Extractor</h1>
    <form @submit.prevent="extractMetadata">
      <div class="form-group">
        <label for="repo-url">Repository URL</label>
        <input
          type="url"
          id="repo-url"
          v-model="repoUrl"
          placeholder="Enter repository URL"
          required
        />
      </div>
      <div class="form-group">
        <label for="schema">Schema</label>
        <select id="schema" v-model="schema" required>
          <option value="maSMP">maSMP</option>
          <option value="codemeta">CODEMETA</option>
        </select>
      </div>
      <div class="form-group">
        <label for="access-token">Access Token (Optional)</label>
        <input
          type="text"
          id="access-token"
          v-model="accessToken"
          placeholder="Enter access token"
        />
      </div>
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Extracting...' : 'Extract' }}
      </button>
    </form>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      repoUrl: '',
      schema: 'maSMP',
      accessToken: '',
      metadata: null,
      error: '',
      isLoading: false,
    };
  },
  methods: {
    async extractMetadata() {
      this.isLoading = true;
      this.error = '';
      this.metadata = null;

      try {
        const response = await fetch('/response.json')
        const data = await response.json();
        this.$emit('metadata-extracted', { metadata: data });
      } catch (err) {
        this.error = 'Failed to extract metadata.';
      } finally {
        this.isLoading = false;
     }
   },
  },
};
</script>

<style scoped>
.home {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  text-align: center;
}
.form-group {
  margin-bottom: 15px;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}
input,
select {
  width: 100%;
  padding: 8px;
  box-sizing: border-box;
}
button {
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  cursor: pointer;
}
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.error-message {
  color: red;
  margin-top: 15px;
}
.metadata-result {
  margin-top: 20px;
  text-align: left;
}
pre {
  background-color: #f4f4f4;
  padding: 10px;
  border-radius: 5px;
}
</style>