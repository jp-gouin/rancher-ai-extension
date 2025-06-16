<template>
  <div class="ai-config">
    <h1 class="title">Rancher AI Assistant - Configuration</h1>

    <form @submit.prevent="saveConfig">
      <div class="form-section">
        <label for="ollamaUrl">Ollama API URL</label>
        <input
          id="ollamaUrl"
          v-model="ollamaUrl"
          type="text"
          placeholder="http://localhost:11434"
          class="input"
        />
      </div>
      <div class="form-section">
      <label for="token">Ollama API Token (optional)</label>
      <input
        id="token"
        v-model="token"
        type="password"
        placeholder="Enter API token"
        class="input"
      />
    </div>

      <div class="form-section">
        <label for="model">Default Model</label>
        <input
          id="model"
          v-model="model"
          type="text"
          placeholder="llama3"
          class="input"
        />
      </div>

      <div class="form-section">
        <label for="mcpServer">MCP Server URL (Tools Backend)</label>
        <input
          id="mcpServer"
          v-model="mcpServer"
          type="text"
          placeholder="https://tools.internal"
          class="input"
        />
      </div>
      <div class="form-section">
        <label for="systemPrompt">System Prompt</label>
        <textarea
          id="systemPrompt"
          v-model="systemPrompt"
          rows="10"
          type="text"
          placeholder="https://tools.internal"
          class="input"
        />
      </div>

      <button type="submit" class="send-button">Save</button>
    </form>
    <div v-if="isLoading" class="thinking-message">
      <div class="dot-loader"></div>
      <span>Rancher AI Assistant is thinking...</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RancherAIAssistantConfiguration',

  data() {
    return {
      ollamaUrl: this.$store.getters['rancher-ai-assistant/ollamaUrl'],
      model: this.$store.getters['rancher-ai-assistant/model'],
      mcpServer: this.$store.getters['rancher-ai-assistant/mcpServer'],
      token: this.$store.getters['rancher-ai-assistant/token'],
      systemPrompt: this.$store.getters['rancher-ai-assistant/systemPrompt'],
    };
  },
  computed: {
    isLoading() {
      return this.$store.state['rancher-ai-assistant'].chat.isLoading;
    }
  },

  methods: {
    saveConfig() {
      this.$store.dispatch('rancher-ai-assistant/configureOllamaTool', {
        ollamaUrl: this.ollamaUrl,
        model: this.model,
        mcpServer: this.mcpServer,
        token: this.token,
        systemPrompt: this.systemPrompt
      });
    }
  }
};
</script>

<style scoped>
.ai-config {
  padding: 20px;
  background-color: var(--body-bg);
  color: var(--primary-text);
}

.title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.form-section {
  margin-bottom: 1rem;
}

label {
  display: block;
  font-weight: 600;
  margin-bottom: 4px;
}

.input {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid var(--border);
  border-radius: 4px;
  background: var(--input-bg);
  color: var(--input-text);
}
.send-button {
  background-color: var(--primary);
  color: var(--link-text);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
}

.send-button:hover {
  background-color: var(--primary-hover);
}
.thinking-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 1rem;
}
.dot-loader {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: var(--primary);
  animation: blink 1s infinite;
}

</style>
