export default {
  messages(state: any) {
    return state.chat.messages;
  },
  ollamaUrl(state: any){ 
    return  state.config.ollamaUrl;
  },
  model(state: any){
    return state.config.model;
  },
  mcpServer(state: any){
    return state.config.mcpServer;
  },
  token(state: any){
    return state.config.token;
  },
  systemPrompt(state: any){
    return state.config.systemPrompt;
  }
};
