(function () {
  const root = document.documentElement; // <html>
  const themeBtn = document.getElementById("theme-toggle");
  const themeIcon = document.getElementById("theme-icon");

  // aplica el modo claro/oscuro visualmente
  function applyTheme(isDark) {
    if (isDark) {
      root.classList.add("theme-dark");  // usamos nuestra propia clase
      localStorage.setItem("theme", "dark");
      if (themeIcon) themeIcon.textContent = "☀️"; // estamos en oscuro -> muestro sol
    } else {
      root.classList.remove("theme-dark");
      localStorage.setItem("theme", "light");
      if (themeIcon) themeIcon.textContent = "🌙"; // estamos en claro -> muestro luna
    }
  }

  // al cargar, mira qué guardamos antes
  const savedTheme = localStorage.getItem("theme");
  if (savedTheme === "dark") {
    applyTheme(true);
  } else {
    applyTheme(false);
  }

  // cuando el usuario hace click
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      const isNowDark = !root.classList.contains("theme-dark");
      applyTheme(isNowDark);
    });
  }
})();




