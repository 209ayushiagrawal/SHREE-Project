document.addEventListener('DOMContentLoaded', function() {
    const buttons = document.querySelectorAll('.status-btn');
    
    // Page load hote hi initial numbers set karein
    updateSummary();

    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const workerId = this.getAttribute('data-worker');
            const status = this.getAttribute('data-status');
            
            // Sabse pas wala button container dhundna
            const btnContainer = this.closest('.attendance-btns');
            
            // 1. HIDDEN INPUT UPDATE (Database ke liye)
            const hiddenInput = document.getElementById('input_' + workerId);
            if(hiddenInput) {
                hiddenInput.value = status;
            }
            
            // 2. UI UPDATE (Colors change karna)
            // Pehle saare buttons se 'active' hatao, fir click wale par lagao
            btnContainer.querySelectorAll('.status-btn').forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            
            // 3. SUMMARY UPDATE (Niche ke cards update karna)
            updateSummary();
        });
    });

    function updateSummary() {
        const rows = document.querySelectorAll('.attendance-table tbody tr');
        const total = rows.length;
        
        // Count statuses
        const present = document.querySelectorAll('.btn-present.active').length;
        const absent = document.querySelectorAll('.btn-absent.active').length;
        const leave = document.querySelectorAll('.btn-leave.active').length;

        // Display update (Check if element exists to avoid errors)
        if(document.getElementById('presentCountDisplay')) 
            document.getElementById('presentCountDisplay').innerText = present;
        
        if(document.getElementById('absentCountDisplay')) 
            document.getElementById('absentCountDisplay').innerText = absent;
        
        if(document.getElementById('leaveCountDisplay')) 
            document.getElementById('leaveCountDisplay').innerText = leave;
        
        // Attendance Rate: Kitne log kaam par aaye (Present / Total)
        if (total > 0 && document.getElementById('rateDisplay')) {
            const rate = Math.round((present / total) * 100);
            document.getElementById('rateDisplay').innerText = rate + '%';
        }
    }
});