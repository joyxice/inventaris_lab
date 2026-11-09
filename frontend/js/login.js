const form = document.querySelector("#loginForm");
const errorBox = document.querySelector("#loginError");
const loginButton = document.querySelector("#loginButton");
const passwordInput = document.querySelector("#password");

document.querySelector("#togglePassword").addEventListener("click", (event) => {
  const show = passwordInput.type === "password";
  passwordInput.type = show ? "text" : "password";
  event.currentTarget.textContent = show ? "Sembunyikan" : "Lihat";
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  errorBox.textContent = "";
  loginButton.disabled = true;
  loginButton.querySelector("span").textContent = "Memeriksa...";

  try {
    const response = await fetch("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: form.elements.username.value.trim(),
        password: form.elements.password.value
      })
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Login gagal");
    window.location.replace("/");
  } catch (error) {
    errorBox.textContent = error.message || "Tidak dapat terhubung ke server.";
    loginButton.disabled = false;
    loginButton.querySelector("span").textContent = "Masuk ke Dashboard";
  }
});
