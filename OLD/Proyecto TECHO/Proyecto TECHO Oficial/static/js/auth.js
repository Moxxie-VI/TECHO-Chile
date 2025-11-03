// auth.js

// Mostrar / ocultar contraseña:
const passWrapper = document.querySelector(".password-wrapper");
if (passWrapper) {
  const passInput = passWrapper.querySelector("input[type='password'], input[type='text']");
  const toggleBtn = passWrapper.querySelector(".toggle-pass");

  let visible = false;
  if (toggleBtn && passInput) {
    toggleBtn.addEventListener("click", () => {
      visible = !visible;
      passInput.type = visible ? "text" : "password";
      toggleBtn.textContent = visible ? "🙈" : "👁";
    });
  }
}
