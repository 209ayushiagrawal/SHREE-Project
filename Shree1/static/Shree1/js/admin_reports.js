document.addEventListener('DOMContentLoaded', function() {
    const generateBtn = document.getElementById("generateBtn");

    if (generateBtn) {
        generateBtn.addEventListener("click", function() {
            // Save original button content
            const originalContent = this.innerHTML;
            
            // Show loading state
            this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Generating...';
            this.style.opacity = "0.7";
            this.disabled = true;

            // Simulate server delay (1.5 seconds)
            setTimeout(() => {
                alert("Success: The requested report has been generated!");
                
                // Restore button state
                this.innerHTML = originalContent;
                this.style.opacity = "1";
                this.disabled = false;
            }, 1500);
        });
    }
});