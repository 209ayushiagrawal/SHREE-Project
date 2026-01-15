document.addEventListener("DOMContentLoaded", () => {
  // 1. Process Salary Button Interaction
  const processButtons = document.querySelectorAll(".btn-process");

  processButtons.forEach((button) => {
    button.addEventListener("click", function () {
      const row = this.closest("tr");
      const employeeName = row.cells[0].innerText;
      const netSalary = row.cells[5].innerText;

      // Change button state to show processing
      this.innerHTML =
        '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
      this.style.opacity = "0.7";
      this.disabled = true;

      // Simulate server request
      setTimeout(() => {
        alert(
          `Payroll successfully processed for ${employeeName}.\nAmount: ${netSalary}`
        );

        // Update button to "Done" state
        this.innerHTML = '<i class="fa-solid fa-check"></i> Processed';
        this.style.backgroundColor = "#f1f5f9";
        this.style.color = "#64748b";
        this.style.border = "none";
      }, 1000);
    });
  });

  // 2. Download Payroll Interaction
  const downloadBtn = document.querySelector(".btn-payroll");

  downloadBtn.addEventListener("click", () => {
    const originalContent = downloadBtn.innerHTML;
    downloadBtn.innerHTML =
      '<i class="fa-solid fa-circle-notch fa-spin"></i> Preparing PDF...';

    setTimeout(() => {
      alert("Your payroll report for the current month is being downloaded.");
      downloadBtn.innerHTML = originalContent;
    }, 1500);
  });
});
