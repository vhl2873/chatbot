# HƯỚNG DẪN TEST HỆ THỐNG RAG

## Các bước test hệ thống

### 1. Upload tài liệu

Sử dụng endpoint `/api/v1/upload-document` để upload file:

**Các file mẫu có sẵn:**
- `sample_document.txt` - Tài liệu về FastAPI
- `sample_ai_ml.txt` - Tài liệu về AI/ML

**Ví dụ sử dụng curl:**
```bash
curl -X POST "https://your-api-url/api/v1/upload-document" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_document.txt"
```

**Ví dụ sử dụng Python:**
```python
import requests

url = "https://your-api-url/api/v1/upload-document"
files = {'file': open('sample_document.txt', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

### 2. Hỏi đáp dựa trên tài liệu

Sau khi upload tài liệu, sử dụng endpoint `/api/v1/chat` để hỏi đáp:

**Ví dụ câu hỏi cho file `sample_document.txt`:**
- "FastAPI có những đặc điểm nổi bật nào?"
- "Làm thế nào để deploy FastAPI?"
- "Best practices khi sử dụng FastAPI là gì?"
- "FastAPI hỗ trợ những loại middleware nào?"
- "Cách tổ chức cấu trúc dự án FastAPI như thế nào?"

**Ví dụ câu hỏi cho file `sample_ai_ml.txt`:**
- "Có những loại máy học nào?"
- "Deep Learning là gì và ứng dụng ra sao?"
- "Quy trình phát triển ML gồm những bước nào?"
- "Các framework ML phổ biến là gì?"
- "Thách thức của AI/ML là gì?"

**Ví dụ sử dụng curl:**
```bash
curl -X POST "https://your-api-url/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"query": "FastAPI có những đặc điểm nổi bật nào?"}'
```

**Ví dụ sử dụng Python:**
```python
import requests

url = "https://your-api-url/api/v1/chat"
data = {"query": "FastAPI có những đặc điểm nổi bật nào?"}
response = requests.post(url, json=data)
print(response.json())
```

### 3. Xem lịch sử chat

Sử dụng endpoint `/api/v1/history` để xem lịch sử các câu hỏi đã hỏi:

```bash
curl "https://your-api-url/api/v1/history?limit=10"
```

### 4. Health check

Kiểm tra trạng thái hệ thống:

```bash
curl "https://your-api-url/api/v1/health"
```

## Lưu ý

- Đảm bảo đã upload ít nhất một tài liệu trước khi hỏi đáp
- Câu hỏi nên liên quan đến nội dung đã upload
- Hệ thống sẽ trả về "Không tìm thấy thông tin" nếu không tìm thấy context liên quan

