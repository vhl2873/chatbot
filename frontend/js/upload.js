// API Base URL - Có thể cấu hình từ config
const API_BASE = '/api/v1';

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const uploadBtn = document.getElementById('uploadBtn');
const progressBar = document.getElementById('progressBar');
const progressFill = document.getElementById('progressFill');
const uploadStatus = document.getElementById('uploadStatus');
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const sendBtnText = document.getElementById('sendBtnText');
const sendLoading = document.getElementById('sendLoading');
const historyToggle = document.getElementById('historyToggle');
const historyList = document.getElementById('historyList');

let selectedFile = null;
let isUploading = false;

// Set welcome time
document.getElementById('welcomeTime').textContent = new Date().toLocaleTimeString('vi-VN');

// Upload Area Events
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    // Validate file type
    const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    const allowedExtensions = ['.pdf', '.txt', '.md', '.docx'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedExtensions.includes(fileExtension)) {
        showUploadStatus('Chỉ hỗ trợ file PDF, TXT, MD, DOCX', 'error');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.classList.add('show');
    uploadBtn.disabled = false;
    uploadStatus.classList.remove('show');
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Upload File
uploadBtn.addEventListener('click', async () => {
    if (!selectedFile || isUploading) return;

    isUploading = true;
    uploadBtn.disabled = true;
    progressBar.classList.add('show');
    progressFill.style.width = '0%';
    uploadStatus.classList.remove('show');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const xhr = new XMLHttpRequest();

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                progressFill.style.width = percentComplete + '%';
            }
        });

        xhr.addEventListener('load', () => {
            if (xhr.status === 201) {
                const response = JSON.parse(xhr.responseText);
                showUploadStatus(
                    `✅ Upload thành công! Đã xử lý ${response.chunks_count} chunks.`,
                    'success'
                );
                chatInput.disabled = false;
                sendBtn.disabled = false;
                selectedFile = null;
                fileInfo.classList.remove('show');
                uploadBtn.disabled = true;
                
                // Add success message to chat
                addMessage('bot', `Tài liệu "${response.doc_id}" đã được upload thành công! Bạn có thể bắt đầu hỏi đáp.`);
            } else {
                const error = JSON.parse(xhr.responseText);
                showUploadStatus(`❌ Lỗi: ${error.detail || 'Upload thất bại'}`, 'error');
            }
            isUploading = false;
            progressBar.classList.remove('show');
        });

        xhr.addEventListener('error', () => {
            showUploadStatus('❌ Lỗi kết nối. Vui lòng thử lại.', 'error');
            isUploading = false;
            uploadBtn.disabled = false;
            progressBar.classList.remove('show');
        });

        xhr.open('POST', `${API_BASE}/upload-document`);
        xhr.send(formData);

    } catch (error) {
        showUploadStatus(`❌ Lỗi: ${error.message}`, 'error');
        isUploading = false;
        uploadBtn.disabled = false;
        progressBar.classList.remove('show');
    }
});

function showUploadStatus(message, type) {
    uploadStatus.textContent = message;
    uploadStatus.className = `upload-status show ${type}`;
}

// Chat Functions
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const textDiv = document.createElement('div');
    textDiv.textContent = text;
    messageDiv.appendChild(textDiv);
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString('vi-VN');
    messageDiv.appendChild(timeDiv);
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query || sendBtn.disabled) return;

    // Add user message
    addMessage('user', query);
    chatInput.value = '';
    sendBtn.disabled = true;
    chatInput.disabled = true;
    sendBtnText.style.display = 'none';
    sendLoading.style.display = 'inline-block';

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query }),
        });

        const data = await response.json();

        if (response.ok) {
            addMessage('bot', data.answer);
            if (data.context_used) {
                // Optionally show context info
                console.log(`Used ${data.chunks_count} chunks for context`);
            }
        } else {
            addMessage('bot', `❌ Lỗi: ${data.detail || 'Không thể xử lý câu hỏi'}`);
        }
    } catch (error) {
        addMessage('bot', `❌ Lỗi kết nối: ${error.message}`);
    } finally {
        sendBtn.disabled = false;
        chatInput.disabled = false;
        sendBtnText.style.display = 'inline';
        sendLoading.style.display = 'none';
        chatInput.focus();
    }
}

// History Functions
let historyVisible = false;

historyToggle.addEventListener('click', async () => {
    if (!historyVisible) {
        await loadHistory();
        historyList.classList.add('show');
        historyToggle.textContent = '📜 Ẩn Lịch sử';
        historyVisible = true;
    } else {
        historyList.classList.remove('show');
        historyToggle.textContent = '📜 Xem Lịch sử';
        historyVisible = false;
    }
});

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/history?limit=10`);
        const data = await response.json();

        historyList.innerHTML = '';

        if (data.history && data.history.length > 0) {
            data.history.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.innerHTML = `
                    <div class="history-question">${item.question}</div>
                    <div class="history-answer">${item.answer}</div>
                `;
                historyItem.addEventListener('click', () => {
                    chatInput.value = item.question;
                    chatInput.focus();
                });
                historyList.appendChild(historyItem);
            });
        } else {
            historyList.innerHTML = '<div style="padding: 20px; text-align: center; color: #666;">Chưa có lịch sử chat</div>';
        }
    } catch (error) {
        historyList.innerHTML = `<div style="padding: 20px; text-align: center; color: #721c24;">Lỗi tải lịch sử: ${error.message}</div>`;
    }
}

