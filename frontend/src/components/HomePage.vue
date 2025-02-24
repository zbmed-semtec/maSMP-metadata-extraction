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
            <option value="CODEMETA">CODEMETA</option>
          </select>
        </div>
        <div class="form-group">
          <label for="access-token">
            Access Token (Optional) 
            <span class="info-icon" @click="showTokenInfo = true">ℹ️</span>
          </label>
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
    <div v-if="showTokenInfo" class="modal-overlay" @click="showTokenInfo = false">
      <div class="modal-content" @click.stop>
        <p>A GitHub access token is required for private repositories and recommended for public repositories to avoid hitting API limits.</p>
        <h3>How to Get a GitHub Access Token?</h3>
          <ol>
            <li>Go to <a href="https://github.com/settings/tokens" target="_blank">GitHub Developer Settings</a></li><br>
            <li>Click <strong>"Generate new token (classic)"</strong></li><br>
            <li>Select <strong>expiration</strong> (optional, but recommended)</li><br>
            <li>Enable the following scopes:
              <ul>
                <li><strong>repo</strong> (if accessing private repositories)</li><br>
                <li><strong>read:org</strong> (if accessing organization repositories)</li><br>
              </ul>
            </li>
            <li>Click <strong>"Generate token"</strong></li><br>
            <li>Copy the token and store it securely (it won't be shown again!)</li><br>
          </ol>
          <button @click="showTokenInfo = false">Close</button>
        </div>
    </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      repoUrl: '',
      schema: 'maSMP',
      accessToken: '',
      error: '',
      isLoading: false,
      showTokenInfo: false,
    };
  },
  methods: {
    async extractMetadata() {
      this.isLoading = true;
      this.error = '';

      try {
        const response = await axios.get(`${process.env.VUE_APP_API_URL}/metadata`, {
          params: { repo_url: this.repoUrl, schema: this.schema, access_token: this.accessToken },
        });
        const data = await response.data;
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
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #dbf2e8;
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
  font-size: 35px;
  color: #42b983;
  text-shadow: -1px -1px 1px rgba(0, 0, 0, 0.6); /* Subtle, smooth text shadow */
  margin-bottom: 30px;
}
.form-group {
  margin-bottom: 15px;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 5px;
  font-weight: 300;
  color: black;
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

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.modal-content h2 {
  margin-top: 0;
}

.modal-content ol {
  text-align: left;
  margin: 20px 0;
}

.modal-content ul {
  margin: 10px 0;
  padding-left: 20px;
}

.modal-content button {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.modal-content button:hover {
  background-color: #36976f;
}

.info-icon {
  cursor: pointer;
  margin-left: 5px;
  font-size: 16px;
}

</style>
