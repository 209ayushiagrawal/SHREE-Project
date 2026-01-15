// Function to handle moving items from Pending to History
function markAsDelivered(checkbox) {
    if (checkbox.checked) {
        // 1. Get the Row
        const row = checkbox.closest("tr");
        
        // 2. Extract Data
        const itemId = row.querySelector(".id-cell").innerText;
        const itemName = row.cells[1].innerText;
        const qty = row.querySelector(".qty-text").innerText;
        // Get today's date for delivery date
        const today = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

        // 3. Add to History Table
        const historyBody = document.getElementById("historyBody");
        const newRow = document.createElement("tr");

        newRow.innerHTML = `
            <td><span class="id-cell">${itemId}</span></td>
            <td>${itemName}</td>
            <td>${qty}</td>
            <td>${today}</td>
            <td><span class="status-badge delivered">Delivered</span></td>
        `;

        // Add fading animation to the old row before removing
        row.style.opacity = "0";
        row.style.transition = "opacity 0.5s";

        setTimeout(() => {
            // Remove from Pending Table
            row.remove();
            
            // Prepend to History Table (so newest is top)
            historyBody.insertBefore(newRow, historyBody.firstChild);
            
            // Update Stats (Optional)
            updateStats();
        }, 500);
    }
}

function updateStats() {
    const pendingCountEl = document.getElementById("pendingCount");
    let count = parseInt(pendingCountEl.innerText);
    if(count > 0) {
        pendingCountEl.innerText = count - 1;
    }
}