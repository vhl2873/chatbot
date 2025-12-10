// Profile page logic
document.addEventListener('DOMContentLoaded', async () => {
    // Kiểm tra authentication với Firebase
    auth.onAuthStateChanged(async (firebaseUser) => {
        if (!firebaseUser) {
            window.location.href = 'index.html';
            return;
        }

        const user = await Auth.getUser();
        
        if (user) {
            document.getElementById('profileName').textContent = user.username || 'N/A';
            document.getElementById('profileEmail').textContent = user.email || 'N/A';
            document.getElementById('infoUsername').textContent = user.username || 'N/A';
            document.getElementById('infoEmail').textContent = user.email || 'N/A';
            document.getElementById('infoPhone').textContent = user.phone || 'N/A';
        } else {
            document.getElementById('profileSection').style.display = 'none';
        }
    });
});

