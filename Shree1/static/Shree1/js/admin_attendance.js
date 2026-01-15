// Function to handle toggle logic
function toggleStatus(button, status) {
    // 1. Get the parent container (.btn-group)
    const parent = button.parentElement;

    // 2. Remove 'active' class from all buttons in this specific group
    const buttons = parent.querySelectorAll('.status-btn');
    buttons.forEach(btn => btn.classList.remove('active'));

    // 3. Add 'active' class to the clicked button
    button.classList.add('active');

    // 4. Trigger Recalculation
    calculateSummary();
}

// Function to calculate summary totals
function calculateSummary() {
    // Count Present buttons that have the 'active' class
    const presentCount = document.querySelectorAll('.status-btn.present.active').length;
    
    // Count Absent buttons that have the 'active' class
    const absentCount = document.querySelectorAll('.status-btn.absent.active').length;

    // Calculate Rate
    const total = presentCount + absentCount;
    const rate = total === 0 ? 0 : Math.round((presentCount / total) * 100);

    // Update the DOM
    document.getElementById('countPresent').innerText = presentCount;
    document.getElementById('countAbsent').innerText = absentCount;
    document.getElementById('attendanceRate').innerText = rate + "%";
}

// Initialize summary on page load
document.addEventListener('DOMContentLoaded', calculateSummary);