const resetBtn = document
  .getElementById("resetBtn")
  .addEventListener("click", function () {
    const currentURL = window.location.pathname;
    const baseURL = window.location.origin + currentURL;
    window.location.href = baseURL;
  });
