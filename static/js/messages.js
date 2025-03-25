document.addEventListener("DOMContentLoaded", function () {
  // Select all alert elements
  const alertList = document.querySelectorAll(".alert");
  // Initialize elements as alerts
  const alerts = [...alertList].map((element) => new bootstrap.Alert(element));

  alertList.forEach((alert, index) => {
    setTimeout(() => {
      alerts[index].close();
    }, 5000); // close alerts after 5 seconds
  });
});
