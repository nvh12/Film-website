// Get elements by their IDs
const loginBtn = document.getElementById("loginBtn");
const loginForm = document.getElementById("loginForm");
const registerBtn = document.getElementById("registerBtn");
const registerForm = document.getElementById("registerForm");
const closeLoginBtn = document.getElementById("closeLoginForm");
const closeRegisterBtn = document.getElementById("closeRegisterForm");

// Show the login form when the login button is clicked
loginBtn.addEventListener("click", function () {
  loginForm.classList.remove("hidden");
});

registerBtn.addEventListener("click", function () {
  loginForm.classList.remove("hidden");
});

// Hide the login form when the close button is clicked
closeLoginBtn.addEventListener("click", function () {
  loginForm.classList.add("hidden");
});

closeRegisterBtn.addEventListener("click", function () {
  loginForm.classList.add("hidden");
});
