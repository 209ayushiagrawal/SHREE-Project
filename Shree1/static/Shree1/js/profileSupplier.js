document.addEventListener("DOMContentLoaded", () => {
  // Save profile
  document.getElementById("profileForm").addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Profile updated successfully!");
  });

  // Change password
  document.getElementById("passwordForm").addEventListener("submit", (e) => {
    e.preventDefault();
    alert("Password updated successfully!");
  });
});
