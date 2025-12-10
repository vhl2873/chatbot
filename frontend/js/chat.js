// Chat page logic
let botId = '';
let chatFace = '';

document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    
    // Kiểm tra authentication với Firebase
    auth.onAuthStateChanged((firebaseUser) => {
        if (!firebaseUser) {
            window.location.href = 'index.html';
            return;
        }

        const selectedChatbot = Utils.getSelectedChatbot();
        botId = selectedChatbot.bot_id;
        chatFace = selectedChatbot.image;

        document.getElementById('chatHeaderTitle').textContent = `Chat với ${selectedChatbot.name}`;

        // Initial message
        addMessage({
            text: `Xin chào, tôi thuộc ${selectedChatbot.name}, tôi có thể giúp gì cho bạn?`,
            isUser: false
        });
    });
});

function addMessage({ text, isUser }) {
    const messagesContainer = document.getElementById('chatMessages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'message-user' : 'message-bot'}`;

    if (!isUser) {
        messageDiv.innerHTML = `
            <img src="${chatFace}" alt="Bot" class="message-avatar">
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${Utils.formatTime(new Date())}</div>
            </div>
        `;
    } else {
        messageDiv.innerHTML = `
            <div class="message-content">
                <div class="message-text">${text}</div>
                <div class="message-time">${Utils.formatTime(new Date())}</div>
            </div>
        `;
    }

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTyping() {
    const messagesContainer = document.getElementById('chatMessages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.className = 'message message-bot';
    typingDiv.innerHTML = `
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    messagesContainer.appendChild(typingDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTyping() {
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message || !botId) return;

    // Add user message
    addMessage({ text: message, isUser: true });
    input.value = '';

    // Disable input
    input.disabled = true;
    document.getElementById('sendButton').disabled = true;
    showTyping();

    try {
        let response;
        
        if (botId === 'tc') {
            response = await API.chatWithCustomModel(botId, message);
        } else if (botId === 'chung') {
            response = await API.chatWithMyLLM(botId, message);
        } else {
            response = await API.chatWithDocuments(botId, message);
        }

        hideTyping();

        if (response.error) {
            if (response.error.includes('Token') || response.error.includes('token')) {
                Auth.logout();
                return;
            }
            throw new Error(response.error);
        }

        const answer = botId === 'tc' || botId === 'chung' 
            ? response.answer.answer 
            : response.answer.output_text;

        addMessage({ text: answer, isUser: false });
    } catch (error) {
        hideTyping();
        addMessage({ 
            text: 'Xin lỗi, có lỗi xảy ra. Vui lòng thử lại.', 
            isUser: false 
        });
    } finally {
        input.disabled = false;
        document.getElementById('sendButton').disabled = false;
        input.focus();
    }
}

function handleChatKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

