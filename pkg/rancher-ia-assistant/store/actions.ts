function timestamp(): string {
    return new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
  
  export default {
    async sendUserMessage({ commit, state }: any, content: string) {
      commit('ADD_MESSAGE', { role: 'user', content, timestamp: timestamp() });
      commit('SET_LOADING', true); // 🔄 Show loader
      const ollamaUrl = state.config.ollamaUrl;
      const token     = state.config.token;
      const model     = state.config.model;
      const mcpServer = state.config.mcpServer;

      await new Promise(r => setTimeout(r, 2000));
      try {
        const res = await fetch(`${ollamaUrl}/api/chat/completions`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              ...(token ? { Authorization: `Bearer ${token}` } : {})
            },
            body: JSON.stringify({
              model,
              messages: state.chat.messages,
              stream: false,
              tool_ids: ['server:0'], // Specify the tool ID if needed
            }),
          });
  
        const data = await res.json();
        let message  = '[No response]';
        console.log(data.choices[0])
        if (data.choices) {
          message = data.choices[0].message.content
        }
        const replyText = message;
        const fullReply = `Rancher AI Assistant: ${replyText}`;
  
        commit('ADD_MESSAGE', { role: 'assistant', content: fullReply, timestamp: timestamp() });
      } catch (e) {
        console.error(e);
        commit('ADD_MESSAGE', {
          role: 'assistant',
          content: 'Rancher AI Assistant: [Error contacting LLM]',
          timestamp: timestamp()
        });
      } finally {
        commit('SET_LOADING', false); // ✅ Hide loader
      }
    },
    // New action to configure Ollama Tool via MCP server
  async configureOllamaTool({ commit, state }: any, content: any) {
    commit('SET_OLLAMA_URL', content.ollamaUrl);
    commit('SET_MODEL', content.model);
    commit('SET_MCP_SERVER', content.mcpServer);
    commit('SET_TOKEN', content.token);
    commit('SET_SPROMPT', content.systemPrompt);
    commit('SET_BACKEND_URL', content.backendUrl);
    commit('SET_LOADING', true); // 🔄 Show loader
  /*   if (state.config.systemPrompt) {
      try {
        const response = await fetch(content.ollamaUrl+'/api/generate', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: state.config.model,
            prompt: state.config.systemPrompt,
          }),
        });

        if (!response.ok) {
          throw new Error(`Failed to generate response: ${response.statusText}`);
        }

        const result = await response.json();
        console.log('Generated response:', result);
        return result;
      } catch (err) {
        console.error('Error generating response:', err);
        throw err;
      } finally {
      
    }
    } */
    commit('SET_LOADING', false); // ✅ Hide loader
    
  },
    initIntroMessage({ commit }: any) {
      commit('ADD_MESSAGE', {
        role: 'assistant',
        content: 'Rancher AI Assistant: Hello! How can I help you today?',
        timestamp: timestamp()
      });
    }
  };
  