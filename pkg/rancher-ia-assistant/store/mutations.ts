import type { ConfigState } from './types';
export default {
    ADD_MESSAGE(state: any, message: { role: string; content: string; timestamp: string }) {
      state.chat.messages.push(message);
    },
  
    SET_LOADING(state: any, isLoading: boolean) {
      state.chat.isLoading = isLoading;
    },
    SET_OLLAMA_URL(state: any, url: any) {
        state.config.ollamaUrl = url;
    },
    SET_MODEL(state: any, model: any) {
        state.config.model = model;
    },
    SET_MCP_SERVER(state: any, server: any) {
        state.config.mcpServer = server;
    },
    SET_TOKEN(state: any, token: string) {
        state.config.token = token;
    },
    SET_SPROMPT(state: any, systemPrompt: string) {
        state.config.systemPrompt = systemPrompt;
    },
  };
  