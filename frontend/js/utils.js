// Utility functions
const Utils = {
  // Validate email
  validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  },

  // Format time
  formatTime(date) {
    return new Date(date).toLocaleTimeString('vi-VN', {
      hour: '2-digit',
      minute: '2-digit'
    });
  },

  // Show error message
  showError(element, message) {
    if (element) {
      element.textContent = message;
      element.style.display = 'block';
      setTimeout(() => {
        element.style.display = 'none';
      }, 5000);
    }
  },

  // Show loading
  showLoading(element) {
    if (element) {
      element.style.display = 'block';
    }
  },

  // Hide loading
  hideLoading(element) {
    if (element) {
      element.style.display = 'none';
    }
  },

  // Get selected chatbot
  getSelectedChatbot() {
    const chatFaceId = parseInt(localStorage.getItem('chatFaceId') || '0');
    return window.CONFIG.chatbots[chatFaceId] || window.CONFIG.chatbots[0];
  },

  // Set selected chatbot
  setSelectedChatbot(chatbotId) {
    localStorage.setItem('chatFaceId', (chatbotId - 1).toString());
  }
};

