// Config sẽ được load từ config.json
window.CONFIG = {
  api: {
    host: "https://chatbot-api-g88f.onrender.com/chat",
    customHost: "https://7128-113-160-170-187.ngrok-free.app/chat"
  },
  chatbots: []
};

// Load config từ JSON file
async function loadConfig() {
  try {
    const response = await fetch('./config.json');
    window.CONFIG = await response.json();
    return window.CONFIG;
  } catch (error) {
    console.error('Error loading config:', error);
    return window.CONFIG;
  }
}

// Initialize config khi page load
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadConfig);
} else {
  loadConfig();
}

