<template>
  <div class="chatbot-container">
    <h1 class="title">Rancher AI Assistant</h1>

    <div class="messages">
      <div
        v-for="(msg, index) in messages"
        :key="index"
        :class="['message', msg.role]"
      >
        <div class="bubble-content">{{ msg.content }}</div>
        <div class="timestamp">{{ msg.timestamp }}</div>
      </div>
    </div>
    <div v-if="isLoading" class="thinking-message">
      <div class="dot-loader"></div>
      <span>Rancher AI Assistant is thinking...</span>
    </div>

    <form @submit.prevent="handleSend" class="input-area">
      <input
        v-model="input"
        type="text"
        placeholder="Ask something..."
        class="input"
      />
      <button type="submit" class="send-button">Send</button>
    </form>
  </div>
</template>

<script>
export default {
  name: 'Chatbot',

  data() {
    return {
      input: ''
    };
  },

  computed: {
    messages() {
      return this.$store.getters['rancher-ai-assistant/messages'];
    },
    isLoading() {
      return this.$store.state['rancher-ai-assistant'].chat.isLoading;
    }
  },

  mounted() {
     if(!this.messages || this.messages.length === 0) {
       // Initialize the intro message only if there are no messages
      this.$store.dispatch('rancher-ai-assistant/initIntroMessage');
     }
    
  },

  methods: {
    async handleSend() {
      const trimmed = this.input.trim();
      if (!trimmed) return;

      await this.$store.dispatch('rancher-ai-assistant/sendUserMessage', trimmed);
      this.input = '';
    }
  }
};
</script>

<style scoped>
.chatbot-container {
  background-color: var(--body-bg);
  color: var(--primary-text);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1rem;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.messages {
  flex: 1;
  overflow-y: auto;
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.message {
  padding: 0.75rem;
  border-radius: 6px;
  max-width: 70%;
  word-wrap: break-word;
  position: relative;
}

.message.user {
  align-self: flex-end;
  background-color: var(--primary);
  color: var(--link-text);
}

.message.assistant {
  align-self: flex-start;
  background-color: var(--accent-bg);
  color: var(--primary-text);
}

.bubble-content {
  white-space: pre-wrap;
}

.timestamp {
  font-size: 0.7rem;
  opacity: 0.6;
  text-align: right;
  margin-top: 0.25rem;
}

.input-area {
  display: flex;
  gap: 0.5rem;
}

.input {
  flex: 1;
  padding: 0.5rem;
  background-color: var(--input-bg);
  border: 1px solid var(--border);
  border-radius: 6px;
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

@keyframes blink {
  0%, 100% { opacity: 0.2; }
  50% { opacity: 1; }
}
</style>
