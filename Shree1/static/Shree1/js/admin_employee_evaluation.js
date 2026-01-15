document.addEventListener("DOMContentLoaded", () => {
  // Star Rating Logic
  document.querySelectorAll(".stars i").forEach((star) => {
    star.addEventListener("click", function () {
      let parent = this.parentElement;
      let allStars = parent.querySelectorAll("i");
      
      // Calculate the index of the clicked star relative to its specific parent container
      let starIndex = Array.from(allStars).indexOf(this);

      allStars.forEach((s, i) => {
        if (i <= starIndex) {
          s.classList.add("checked");
        } else {
          s.classList.remove("checked");
        }
      });
    });
  });

  // Save Button Logic
  const saveBtn = document.querySelector(".btn-save");
  if (saveBtn) {
    saveBtn.addEventListener("click", () => {
      alert("Evaluations saved successfully!");
    });
  }
});