import { CoreStoreSpecifics, CoreStoreConfig } from '@shell/core/types';
import getters from './getters';
import mutations from './mutations';
import actions from './actions';

const PRODUCT_NAME = 'rancher-ai-assistant'; // ← this must match your namespace

const storeFactory = (): CoreStoreSpecifics => {
  return {
    state() {
      return { 
        chat: { messages: [], isLoading: false },
        config: {
            ollamaUrl: 'http://localhost:11434',
            token: '',
            model: 'qwen3:0.6b',
            mcpServer: '',
            systemPrompt: 'You are a helpful AI assistant integrated with Rancher. Your role is to assist users with their Rancher-related queries and tasks. Please provide clear and concise answers, and if you do not know the answer, suggest that the user consult the Rancher documentation or support resources. always answer in Markdown format, and use code blocks for any code examples or commands. If the user asks about Rancher AI Assistant, explain that it is an AI assistant integrated with Rancher to help users with their Rancher-related queries and tasks.'
        }
      };
    },
    getters,
    mutations,
    actions
  };
};

const config: CoreStoreConfig = {
  namespace: PRODUCT_NAME // ← this is what defines the full path
};
export default {
  specifics: storeFactory(),
  config
};
