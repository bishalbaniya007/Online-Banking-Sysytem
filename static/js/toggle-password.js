document.addEventListener("DOMContentLoaded", () => {
  const toggles = document.querySelectorAll(".toggle-password");

  toggles.forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = btn.previousElementSibling;
      const icon = btn.querySelector(".eye-icon");

      if (input.type === "password") {
        input.type = "text";
        icon.textContent = "🙈";
        btn.setAttribute("aria-label", "Hide password");
      } else {
        input.type = "password";
        icon.textContent = "👁️";
        btn.setAttribute("aria-label", "Show password");
      }
    });
  });
});