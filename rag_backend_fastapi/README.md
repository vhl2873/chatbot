# RAG Backend - FastAPI + Firebase + ChromaDB

Backend FastAPI hoàn chỉnh với RAG (Retrieval-Augmented Generation) tích hợp Firebase và ChromaDB.

## 🚀 Cấu trúc Project

```
rag_backend_fastapi/
├── main.py                  # FastAPI application entry point
├── config.py                # Configuration settings
├── api/
│   ├── routes.py           # API endpoints
│   └── models.py           # Pydantic models
├── services/
│   ├── firebase_service.py    # Firebase operations
│   ├── rag_service.py         # RAG pipeline
│   ├── embedding_service.py   # Embeddings
│   ├── vectorstore_service.py # ChromaDB operations
│   ├── prompt_service.py      # Prompt templates
│   └── text_splitter.py      # Text chunking
├── requirements.txt
└── README.md
```

## 📦 Cài đặt

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Cấu hình Firebase

1. Tải `serviceAccountKey.json` từ Firebase Console
2. Đặt file vào thư mục `rag_backend_fastapi/`

**Lưu ý:** Firebase Storage là tùy chọn. Nếu không cấu hình Storage bucket, file upload sẽ trả về URL local.

### 3. Cấu hình Environment Variables

Tạo file `.env` trong thư mục `rag_backend_fastapi/`:

```env
# Bắt buộc
FIREBASE_CREDENTIALS_PATH=serviceAccountKey.json
GOOGLE_API_KEY=your-google-api-key

# Tùy chọn - Firebase Storage (bỏ qua nếu không dùng)
# FIREBASE_STORAGE_BUCKET=your-project.firebasestorage.app

# Tùy chọn - LLM và Embedding
LLM_MODEL=gemini-pro
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Tùy chọn - RAG Config
TOP_K_CHUNKS=5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

**Lưu ý:**
- `FIREBASE_CREDENTIALS_PATH`: Đường dẫn đến file `serviceAccountKey.json` (mặc định: `serviceAccountKey.json`)
- `GOOGLE_API_KEY`: API key cho Gemini LLM (bắt buộc để sử dụng chat)
- `FIREBASE_STORAGE_BUCKET`: Chỉ cần nếu muốn lưu file lên Firebase Storage (tùy chọn)

### 4. Chạy server

```bash
python main.py
```

Hoặc với uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Endpoints

### 1. Upload Document

**POST** `/api/v1/upload-document`

Upload file và xử lý RAG pipeline.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (PDF, TXT, MD, DOCX)

**Response:**
```json
{
    "doc_id": "uuid",
    "file_url": "https://...",
    "chunks_count": 10,
    "status": "success",
    "message": "Document uploaded and processed successfully"
}
```

### 2. Chat với RAG

**POST** `/api/v1/chat`

**Request:**
```json
{
    "query": "Câu hỏi của bạn"
}
```

**Response:**
```json
{
    "answer": "Câu trả lời từ LLM",
    "context_used": true,
    "chunks_count": 5
}
```

### 3. Lấy Lịch sử Chat

**GET** `/api/v1/history?limit=50`

**Response:**
```json
{
    "history": [
        {
            "id": "uuid",
            "question": "Câu hỏi",
            "answer": "Câu trả lời",
            "created_at": "2024-01-01T00:00:00"
        }
    ],
    "count": 50
}
```

### 4. Health Check

**GET** `/api/v1/health`

**Response:**
```json
{
    "status": "healthy",
    "vectorstore": {
        "total_chunks": 100
    }
}
```

## 🔄 RAG Pipeline

1. **Upload Document:**
   - File → Firebase Storage (nếu được cấu hình) hoặc local
   - Metadata → Firestore `documents/`
   - Text → Chunk
   - Chunks → Embedding
   - Vectors → Firestore `chunks/` + ChromaDB

2. **Query:**
   - Query → Embedding
   - Embedding → ANN Search (ChromaDB)
   - Top-K Chunks → Firestore
   - Context + Query → Prompt
   - Prompt → LLM (Gemini)
   - Answer → Firestore `history/`

## 🔥 Firebase Collections

- `documents/` - Document metadata
- `chunks/` - Text chunks with vectors
- `history/` - Chat history

## 📖 API Documentation

Sau khi chạy server, truy cập:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## ⚙️ Tính năng

- ✅ FastAPI với async/await support
- ✅ Automatic API documentation (Swagger/ReDoc)
- ✅ Pydantic validation
- ✅ CORS middleware
- ✅ Error handling
- ✅ Type hints đầy đủ

## 🆚 So sánh với Django version

| Tính năng | Django | FastAPI |
|-----------|--------|---------|
| Framework | Django REST | FastAPI |
| Performance | Good | Excellent (async) |
| Documentation | Manual | Auto-generated |
| Type Safety | Limited | Full (Pydantic) |
| Async Support | Limited | Native |
| API Docs | Manual | Swagger/ReDoc |

## 📝 Lưu ý

- Đảm bảo có `serviceAccountKey.json` trong thư mục root
- ChromaDB sẽ tự tạo thư mục `chroma_db/`
- Cần Google API Key để sử dụng Gemini LLM
- Python 3.8+ required

## 🐛 Troubleshooting

### Port đã được sử dụng
```bash
uvicorn main:app --port 8001
```

### Firebase không khởi tạo
- Kiểm tra đường dẫn `serviceAccountKey.json`
- Kiểm tra quyền truy cập Firebase

### ChromaDB lỗi
- Đảm bảo có quyền ghi trong thư mục
- Xóa thư mục `chroma_db/` và chạy lại

