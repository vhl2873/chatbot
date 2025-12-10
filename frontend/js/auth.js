// Authentication utilities với Firebase
const Auth = {
  // Lưu user vào localStorage (để tương thích với code hiện tại)
  _saveUserToLocal(user) {
    localStorage.setItem('user', JSON.stringify(user));
  },

  // Lấy user hiện tại từ Firebase hoặc localStorage
  async getUser() {
    const currentUser = auth.currentUser;
    if (currentUser) {
      // Lấy thông tin bổ sung từ Firestore
      try {
        const userDoc = await db.collection('users').doc(currentUser.uid).get();
        if (userDoc.exists) {
          const userData = userDoc.data();
          return {
            uid: currentUser.uid,
            email: currentUser.email,
            username: userData.username || currentUser.displayName || '',
            phone: userData.phone || ''
          };
        } else {
          // Nếu chưa có trong Firestore, trả về thông tin cơ bản
          return {
            uid: currentUser.uid,
            email: currentUser.email,
            username: currentUser.displayName || '',
            phone: ''
          };
        }
      } catch (error) {
        console.error('Error getting user data:', error);
        // Fallback về localStorage nếu có
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
      }
    }
    // Fallback về localStorage
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  },

  // Lấy Firebase ID token
  async getToken() {
    const currentUser = auth.currentUser;
    if (currentUser) {
      try {
        return await currentUser.getIdToken();
      } catch (error) {
        console.error('Error getting token:', error);
        return null;
      }
    }
    // Fallback về localStorage
    return localStorage.getItem('token');
  },

  // Kiểm tra đã đăng nhập
  isAuthenticated() {
    return auth.currentUser !== null;
  },

  // Đăng nhập với Firebase
  async loginWithFirebase(email, password) {
    try {
      const userCredential = await auth.signInWithEmailAndPassword(email, password);
      const user = await this.getUser();
      this._saveUserToLocal(user);
      return userCredential;
    } catch (error) {
      throw error;
    }
  },

  // Đăng ký với Firebase
  async registerWithFirebase(email, password, username, phone) {
    try {
      // Tạo user trong Firebase Auth
      const userCredential = await auth.createUserWithEmailAndPassword(email, password);
      const user = userCredential.user;

      // Lưu thông tin bổ sung vào Firestore
      await db.collection('users').doc(user.uid).set({
        username: username,
        phone: phone,
        email: email,
        createdAt: firebase.firestore.FieldValue.serverTimestamp()
      });

      // Lưu vào localStorage
      const userData = {
        uid: user.uid,
        email: user.email,
        username: username,
        phone: phone
      };
      this._saveUserToLocal(userData);

      return userCredential;
    } catch (error) {
      throw error;
    }
  },

  // Đăng xuất
  async logout() {
    try {
      await auth.signOut();
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      window.location.href = 'index.html';
    } catch (error) {
      console.error('Error signing out:', error);
      // Vẫn redirect dù có lỗi
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      window.location.href = 'index.html';
    }
  },

  // Lắng nghe thay đổi trạng thái authentication
  onAuthStateChanged(callback) {
    return auth.onAuthStateChanged(callback);
  }
};

