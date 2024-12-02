// Get elements by their IDs
const loginBtn = document.getElementById("loginBtn");
const loginForm = document.getElementById("loginForm");
const registerBtn = document.getElementById("registerBtn");
const registerForm = document.getElementById("registerForm");
const closeLoginBtn = document.getElementById("closeLoginForm");
const closeRegisterBtn = document.getElementById("closeRegisterForm");
const changeToLoginBtn = document.getElementById("changeToLoginButton");
const changeToRegisterBtn = document.getElementById("changeToRegisterButton");
if (changeToLoginBtn && changeToRegisterBtn) console.log("done");
else console.log("None");

// Show the login form when the login button is clicked
loginBtn.addEventListener("click", function () {
  loginForm.classList.remove("hidden");
});

registerBtn.addEventListener("click", function () {
  registerForm.classList.remove("hidden");
});

// Hide the login form when the close button is clicked
closeLoginBtn.addEventListener("click", function () {
  loginForm.classList.add("hidden");
});

closeRegisterBtn.addEventListener("click", function () {
  registerForm.classList.add("hidden");
});

// Change form state
changeToLoginBtn.addEventListener("click", function () {
  registerForm.classList.add("hidden");
  loginForm.classList.remove("hidden");
});

changeToRegisterBtn.addEventListener("click", function () {
  registerForm.classList.remove("hidden");
  loginForm.classList.add("hidden");
});
