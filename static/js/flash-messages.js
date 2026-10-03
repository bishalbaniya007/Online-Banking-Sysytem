document.addEventListener("DOMContentLoaded", () => {
  const alerts = document.querySelectorAll(".flash-alert");

  alerts.forEach((alert) => {
    setTimeout(() => {
      alert.classList.add("flash-hide");

      // remove from DOM after the fade-out transition finishes
      alert.addEventListener("transitionend", () => alert.remove());
    }, 2500); // time visible before it starts fading, in ms
  });
});