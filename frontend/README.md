# Chatbot Web Frontend (HTML/CSS/JS)

Ứng dụng web chatbot cho Đại học Vinh, được xây dựng với HTML, CSS, JavaScript thuần và JSON.

## Cấu trúc dự án

```
frontend/
├── index.html          # Trang đăng nhập
├── register.html       # Trang đăng ký
├── home.html           # Trang chủ (chọn chatbot)
├── chat.html           # Trang chat
├── profile.html        # Trang hồ sơ
├── config.json         # Cấu hình API và chatbots
├── css/
│   └── style.css       # Styles cho tất cả các trang
└── js/
    ├── config.js       # Load và quản lý config
    ├── auth.js         # Xác thực người dùng
    ├── api.js          # Gọi API
    ├── utils.js        # Utility functions
    ├── login.js        # Logic trang đăng nhập
    ├── register.js     # Logic trang đăng ký
    ├── home.js         # Logic trang chủ
    ├── chat.js         # Logic trang chat
    └── profile.js      # Logic trang hồ sơ
```

## Cách sử dụng

### Chạy trực tiếp

Mở file `index.html` trong trình duyệt hoặc sử dụng local server:

```bash
# Sử dụng Python
python -m http.server 8000

# Sử dụng Node.js (nếu có http-server)
npx http-server -p 8000

# Sử dụng PHP
php -S localhost:8000
```

Sau đó truy cập `http://localhost:8000`

### Cấu hình

Chỉnh sửa file `config.json` để thay đổi:
- API endpoints
- Danh sách chatbots
- Thông tin chatbot

## Tính năng

- ✅ Đăng nhập/Đăng ký
- ✅ Chọn chatbot từ danh sách
- ✅ Giao diện chat với typing indicator
- ✅ Quản lý hồ sơ người dùng
- ✅ Responsive design
- ✅ Authentication với JWT
- ✅ Lưu trữ local state với localStorage

## Công nghệ sử dụng

- HTML5
- CSS3
- JavaScript (ES6+)
- JSON
- LocalStorage API
- Fetch API

## Lưu ý

- Cần chạy backend API trước khi sử dụng
- Cập nhật API endpoints trong `config.json` nếu cần
- Trình duyệt cần hỗ trợ ES6+ và Fetch API
