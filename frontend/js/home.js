// Home page logic
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    
    // Kiểm tra authentication với Firebase
    auth.onAuthStateChanged(async (firebaseUser) => {
        if (!firebaseUser) {
            window.location.href = 'index.html';
            return;
        }

        const user = await Auth.getUser();
        const selectedChatbot = Utils.getSelectedChatbot();

        // Update UI với chatbot đã chọn
        document.getElementById('homeSubtitle').textContent = selectedChatbot.name;
        document.getElementById('homeSubtitle').style.color = selectedChatbot.primary;
        document.getElementById('homeTitle').style.color = selectedChatbot.primary;
        document.getElementById('homeAvatar').src = selectedChatbot.image;
        document.getElementById('startButton').style.backgroundColor = selectedChatbot.primary;

        // Render chatbot list
        const chatFacesList = document.getElementById('chatFacesList');
        window.CONFIG.chatbots.forEach(chatbot => {
            if (chatbot.id !== selectedChatbot.id) {
                const button = document.createElement('button');
                button.className = 'chat-face-button';
                button.innerHTML = `<img src="${chatbot.image}" alt="${chatbot.name}" class="chat-face-icon">`;
                button.onclick = () => {
                    Utils.setSelectedChatbot(chatbot.id);
                    location.reload();
                };
                chatFacesList.appendChild(button);
            }
        });

        // Start button
        document.getElementById('startButton').onclick = () => {
            window.location.href = 'chat.html';
        };

        // User info
        if (user) {
            document.getElementById('userInfoCard').style.display = 'block';
            document.getElementById('userName').textContent = `Tên: ${user.username || 'N/A'}`;
            document.getElementById('userEmail').textContent = `Email: ${user.email || 'N/A'}`;
            document.getElementById('userPhone').textContent = `Số điện thoại: ${user.phone || 'N/A'}`;
        }
    });
});

