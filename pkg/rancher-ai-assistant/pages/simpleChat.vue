<template>
  <div class="chat-container">
    <h1 class="title">✨ Rancher AI Assistant</h1>
    <main class="chat-main">
      <div v-for="(msg, i) in messages" :key="i" class="message" :class="msg.role">
        <div v-if="msg.role == 'user'" class="bubble">{{ msg.content }}</div>
        <div v-else class="bubble message assistant">
          <div v-if="msg.streamedThinking" class="thinking" :class="{ streamed: msg.streaming }" v-on:click="msg.expanded=!msg.expanded">
            🤔 <strong>Thinking...  (click to open) ⬇ </strong>
            <div v-show="msg.expanded" class="thinking-details">{{ msg.streamedThinking }}</div>
          </div>
          <div v-if="msg.streamedResponse" :class="{ streamed: msg.streaming }" >
            <hr class="rounded">
            <span v-html="msg.content"></span>
          </div>
        </div>
      </div>
    </main>

    <footer class="chat-footer">
      <input
        v-model="input"
        @keyup.enter="sendPrompt"
        placeholder="Type your prompt..."
        class="input"
      />
      <button @click="sendPrompt" class="send-button">Send</button>
    </footer>
  </div>
</template>

<script>
import Markdown from '@shell/components/Markdown';
import MarkdownIt from 'markdown-it'

export default {
  name: "Chat",
  components: { Markdown },
  data() {
    return {
      input: "",
      messages: [],
      streaming: false,
      backendurl: this.$store.getters['rancher-ai-assistant/backend'],
      md: new MarkdownIt({
        html: true,
        breaks: true,
        linkify: true,
        typographer: true,
      }),
    };
  },
  methods: {
    sendPrompt() {
      if (!this.input.trim()) return;
      const prompt = this.input.trim();
      
      // Add user message
      this.messages.push({ role: "user", content: prompt, streaming: false });
      this.messages.push({ role: "assistant", content: "", streamedThinking: "Connecting...",streamedResponse: "" ,isThinking: true, streaming: false, expanded: true });
      this.input = "";
      // Connect to the eventsource using the window location to get the correct URL
      const url = window.location.origin;
      const eventSource = new EventSource(url+"/api/v1/namespaces/suseai/services/http:rancher-ai-backend:80/proxy/chat?prompt=" + encodeURIComponent(prompt), { withCredentials: true });
      //const eventSource = new EventSource("http://localhost:8000/chat?prompt=" + encodeURIComponent(prompt), { withCredentials: true });
      eventSource.onmessage = (event) => {
        let currentMessage = this.messages[this.messages.length - 1];
        currentMessage.streaming = true;
        if (currentMessage.streamedThinking == "Connecting...") {
            currentMessage.streamedThinking = "";
        }
        const line = event.data;
       // const line = decoder.decode(value, { stream: true });
        if (line.includes('<think>')) {
          currentMessage.isThinking = true;
          return;
        }
        if (line.includes('</think>')) {
          currentMessage.isThinking = false;
          return;
        }
        if(line.includes('[END]]')){
          //currentMessage.content = this.md.render(currentMessage.streamedResponse);
          currentMessage.streaming = false;
          //currentMessage.streamedResponse = "";
          return; 
        }

        if (currentMessage.isThinking) { 
          currentMessage.streamedThinking += line
        }else {
          currentMessage.streamedResponse += line;
          currentMessage.content = this.md.render(currentMessage.streamedResponse);
        }
        
      };

      eventSource.onerror = () => {
        eventSource.close();
        let currentMessage = this.messages[this.messages.length - 1];
        currentMessage.isThinking = false;
        if (currentMessage.streamedResponse == "") {
          currentMessage.content = "Error: Unable to connect to the server.";
          currentMessage.streamedResponse = currentMessage.content;
        }
        currentMessage.streaming = false;
      };

      // Optional auto-scroll
      this.$nextTick(() => {
       const main = document.querySelector(".chat-main");
       main.scrollTop = main.scrollHeight;
      });
    },
  },
};
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  font-family: Arial, sans-serif;
  background: var(--body-bg);;
  color: white;
}

.title {
  font-size: 1.5rem;
  margin-bottom: 1rem;
}

.chat-main {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: var(--body-bg);;
}

.message {
  margin-bottom: 12px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message.assistant {
  justify-content: flex-start;
  display: inline-block;
}

.bubble {
  padding: 10px 14px;
  border-radius: 16px;
  max-width: 60%;
  word-wrap: break-word;
}
.thinking-details {
  margin-top: 6px;
  font-family: monospace;
  font-size: 0.85rem;
  color: var(--body-text);
}
.thinking {
  min-width: 15rem;
}

.user .bubble {
  background: #007acc;
  color: white;
}

.assistant .bubble {
  color: var(--body-text);
  min-width: 20rem;
}

.chat-footer {
  display: flex;
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
hr.rounded {
  border-top: 2px solid #bbb;
  border-radius: 5px;
}

.streamed {
  animation: pulse 1.5s infinite alternate;
}

@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  100% {
    opacity: 1;
  }
}
</style>
