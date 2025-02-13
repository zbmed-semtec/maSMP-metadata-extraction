<template>
  <div class="home">
    <div class="card">
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
  </div>
</template>

<script>
export default {
  data() {
    return {
      repoUrl: '',
      schema: 'maSMP',
      accessToken: '',
      error: '',
      isLoading: false,
    };
  },
  methods: {
    async extractMetadata() {
      this.isLoading = true;
      this.error = '';

      try {
        const response = await fetch('/response_1.json');
        const data = await response.json();
        this.$router.push({
          name: 'MetadataDisplay',
          query: { metadata: JSON.stringify(data) },
        });
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
body {
  font-family: 'Inter', sans-serif;
  background-color: #f4f7fc;
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.home {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 85vh;
  padding: 20px;
}
.card {
  padding: 30px;
  border-radius: 12px;
  box-shadow: 5px 5px 15px rgba(0, 0, 0, 0.2);
  max-width: 500px;
  width: 100%;
  text-align: center;
  background: linear-gradient(480deg, #ffffff, #f2f5f4);
}
h1 {
  color: #333;
  margin-bottom: 30px;
}
.form-group {
  margin-bottom: 15px;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: 550;
  color: #333;
}
input,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 8px;
  box-sizing: border-box;
  font-size: 16px;
  background-color: #fff;
}
button {
  width: 100%;
  padding: 12px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s;
}
button:hover {
  background-color: #36976f;
}
button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}
.error-message {
  color: red;
  margin-top: 15px;
  font-weight: 600;
}
@media (max-width: 600px) {
  .card {
    padding: 20px;
  }
}
</style>
