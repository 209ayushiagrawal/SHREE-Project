// --- REDIRECTION LOGIC (Put this in your Login/Signup JS) ---
/*
function handleLogin() {
    // After validating credentials...
    window.location.href = "wardenDashboard.html";
}
*/

// --- DASHBOARD INTERACTIVITY ---
document.addEventListener('DOMContentLoaded', () => {
    
    // Logout Functionality
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', () => {
            if(confirm("Are you sure you want to logout?")) {
                // Redirect back to login page
                window.location.href = "login.html"; 
            }
        });
    }

    // Example: Handling Leave Approvals
    const approveButtons = document.querySelectorAll('.btn-approve');
    approveButtons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const card = e.target.closest('.leave-item');
            alert('Request Approved Successfully!');
            card.style.opacity = '0.5';
            e.target.disabled = true;
        });
    });

    // Sidebar navigation highlight
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.addEventListener('click', function() {
            navItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
});