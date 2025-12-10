// Login page logic với Firebase
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    
    // Kiểm tra trạng thái authentication
    auth.onAuthStateChanged((user) => {
        if (user) {
            window.location.href = 'home.html';
        }
    });

    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const loginButton = document.getElementById('loginButton');

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        loginButton.disabled = true;
        loginButton.textContent = 'Đang đăng nhập...';
        Utils.showError(errorMessage, ''); // Clear error
        
        try {
            await Auth.loginWithFirebase(email, password);
            // Redirect sẽ được xử lý bởi onAuthStateChanged
            window.location.href = 'home.html';
        } catch (error) {
            let errorMessageText = 'Có lỗi xảy ra, vui lòng thử lại';
            
            // Xử lý các lỗi Firebase phổ biến
            switch (error.code) {
                case 'auth/user-not-found':
                    errorMessageText = 'Email không tồn tại';
                    break;
                case 'auth/wrong-password':
                    errorMessageText = 'Mật khẩu không đúng';
                    break;
                case 'auth/invalid-email':
                    errorMessageText = 'Email không hợp lệ';
                    break;
                case 'auth/user-disabled':
                    errorMessageText = 'Tài khoản đã bị vô hiệu hóa';
                    break;
                case 'auth/too-many-requests':
                    errorMessageText = 'Quá nhiều lần thử. Vui lòng thử lại sau';
                    break;
                case 'auth/network-request-failed':
                    errorMessageText = 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối';
                    break;
                default:
                    errorMessageText = error.message || 'Đăng nhập thất bại';
            }
            
            Utils.showError(errorMessage, errorMessageText);
        } finally {
            loginButton.disabled = false;
            loginButton.textContent = 'Đăng nhập';
        }
    });
});

