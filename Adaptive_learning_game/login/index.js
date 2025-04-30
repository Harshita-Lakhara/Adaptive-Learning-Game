function startGame() {
  // Redirect to subjects.html
  window.location.href = "subjects.html";
}
document.addEventListener("DOMContentLoaded", function () {
  let username = sessionStorage.getItem("username");

  if (username) {
      document.getElementById("welcome-message").innerText = `Welcome, ${username}!`;
  } else {
      window.location.href = "login.html";  // Redirect to login if not logged in
  }
});



  AOS.init();

