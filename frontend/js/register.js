// Register page logic với Firebase
document.addEventListener('DOMContentLoaded', async () => {
    await loadConfig();
    
    // Kiểm tra trạng thái authentication
    auth.onAuthStateChanged((user) => {
        if (user) {
            window.location.href = 'home.html';
        }
    });

    const registerForm = document.getElementById('registerForm');
    const errorMessage = document.getElementById('errorMessage');
    const registerButton = document.getElementById('registerButton');

    // Validate form
    function validateForm() {
        const email = document.getElementById('email').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        const phone = document.getElementById('phone').value;

        let isValid = true;

        // Clear previous errors
        ['emailError', 'usernameError', 'passwordError', 'confirmPasswordError', 'phoneError'].forEach(id => {
            const errorEl = document.getElementById(id);
            if (errorEl) errorEl.style.display = 'none';
        });

        // Validate email
        if (!email) {
            Utils.showError(document.getElementById('emailError'), 'Email không được để trống');
            isValid = false;
        } else if (!Utils.validateEmail(email)) {
            Utils.showError(document.getElementById('emailError'), 'Email không hợp lệ');
            isValid = false;
        }

        // Validate username
        if (!username) {
            Utils.showError(document.getElementById('usernameError'), 'Tên người dùng không được để trống');
            isValid = false;
        }

        // Validate password
        if (!password) {
            Utils.showError(document.getElementById('passwordError'), 'Mật khẩu không được để trống');
            isValid = false;
        } else if (password.length < 6) {
            Utils.showError(document.getElementById('passwordError'), 'Mật khẩu phải có ít nhất 6 ký tự');
            isValid = false;
        }

        // Validate confirm password
        if (!confirmPassword) {
            Utils.showError(document.getElementById('confirmPasswordError'), 'Xác nhận mật khẩu không được để trống');
            isValid = false;
        } else if (password !== confirmPassword) {
            Utils.showError(document.getElementById('confirmPasswordError'), 'Mật khẩu không trùng khớp');
            isValid = false;
        }

        // Validate phone
        if (!phone) {
            Utils.showError(document.getElementById('phoneError'), 'Số điện thoại không được để trống');
            isValid = false;
        }

        return isValid;
    }

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        if (!validateForm()) return;

        const email = document.getElementById('email').value;
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;
        const phone = document.getElementById('phone').value;

        registerButton.disabled = true;
        registerButton.textContent = 'Đang đăng ký...';
        Utils.showError(errorMessage, ''); // Clear error

        try {
            await Auth.registerWithFirebase(email, password, username, phone);
            // Redirect sẽ được xử lý bởi onAuthStateChanged
            window.location.href = 'home.html';
        } catch (error) {
            let errorMessageText = 'Có lỗi xảy ra, vui lòng thử lại';
            
            // Xử lý các lỗi Firebase phổ biến
            switch (error.code) {
                case 'auth/email-already-in-use':
                    errorMessageText = 'Email đã được sử dụng';
                    Utils.showError(document.getElementById('emailError'), 'Email đã được sử dụng');
                    break;
                case 'auth/invalid-email':
                    errorMessageText = 'Email không hợp lệ';
                    Utils.showError(document.getElementById('emailError'), 'Email không hợp lệ');
                    break;
                case 'auth/weak-password':
                    errorMessageText = 'Mật khẩu quá yếu. Vui lòng sử dụng mật khẩu mạnh hơn';
                    Utils.showError(document.getElementById('passwordError'), 'Mật khẩu quá yếu');
                    break;
                case 'auth/network-request-failed':
                    errorMessageText = 'Lỗi kết nối mạng. Vui lòng kiểm tra kết nối';
                    break;
                default:
                    errorMessageText = error.message || 'Đăng ký thất bại';
            }
            
            Utils.showError(errorMessage, errorMessageText);
        } finally {
            registerButton.disabled = false;
            registerButton.textContent = 'Tạo tài khoản';
        }
    });
});

