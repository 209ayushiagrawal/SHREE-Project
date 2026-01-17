#supplier_profile.js
document.addEventListener("DOMContentLoaded", () => {
  // --- Handle Profile Update ---
  const profileForm = document.querySelector(".profile-form");
  const saveProfileBtn = profileForm
    ? profileForm.querySelector(".btn-primary")
    : null;

  if (saveProfileBtn) {
    saveProfileBtn.addEventListener("click", (e) => {
      e.preventDefault();

      // Logic to collect data could go here
      // const fullName = profileForm.querySelector('input[type="text"]').value;

      alert("Supplier profile details updated successfully!");
    });
  }

  // --- Handle Password Update ---
  const passwordSection = document.querySelector(".password-section");
  const updatePasswordBtn = passwordSection
    ? passwordSection.querySelector(".btn-primary")
    : null;

  if (updatePasswordBtn) {
    updatePasswordBtn.addEventListener("click", (e) => {
      e.preventDefault();

      const inputs = passwordSection.querySelectorAll("input");
      const currentPass = inputs[0].value;
      const newPass = inputs[1].value;
      const confirmPass = inputs[2].value;

      // Basic Validation
      if (!currentPass || !newPass || !confirmPass) {
        alert("Please fill in all password fields.");
        return;
      }

      if (newPass !== confirmPass) {
        alert("New password and Confirm password do not match!");
        return;
      }

      if (newPass.length < 6) {
        alert("New password must be at least 6 characters long.");
        return;
      }

      // Success simulation
      alert("Password updated successfully!");

      // Clear fields after success
      inputs.forEach((input) => (input.value = ""));
    });
  }
});