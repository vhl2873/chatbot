// API utilities
const API = {
  // Gọi API với authentication
  async request(endpoint, options = {}) {
    // Lấy Firebase ID token
    const token = await Auth.getToken();
    const baseUrl = endpoint.includes('custom') || endpoint.includes('my_llm') 
      ? window.CONFIG.api.customHost 
      : window.CONFIG.api.host;

    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Bearer ${token}` })
      }
    };

    const response = await fetch(`${baseUrl}/${endpoint}`, {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...(options.headers || {})
      }
    });

    return response.json();
  },

  // Đăng nhập
  async login(email, password) {
    return this.request('login', {
      method: 'POST',
      body: JSON.stringify({ email, password })
    });
  },

  // Đăng ký
  async register(data) {
    return this.request('register', {
      method: 'POST',
      body: JSON.stringify(data)
    });
  },

  // Chat với documents
  async chatWithDocuments(botId, question) {
    return this.request('chat_with_documents', {
      method: 'POST',
      body: JSON.stringify({ bot_id: botId, question })
    });
  },

  // Chat với custom model
  async chatWithCustomModel(botId, question) {
    return this.request('chat_with_custom_model', {
      method: 'POST',
      body: JSON.stringify({ bot_id: botId, question })
    });
  },

  // Chat với custom LLM
  async chatWithMyLLM(botId, question) {
    return this.request('chat_with_my_llm', {
      method: 'POST',
      body: JSON.stringify({ bot_id: botId, question })
    });
  }
};

