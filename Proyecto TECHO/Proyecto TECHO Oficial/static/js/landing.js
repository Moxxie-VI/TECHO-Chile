// ====== Estado inicial desde localStorage ======
const htmlTag = document.documentElement; // <html ...>
const btnTheme = document.getElementById("btn-theme");
const btnFontPlus = document.getElementById("btn-font-plus");
const btnFontMinus = document.getElementById("btn-font-minus");

// Cargar tema guardado
const savedTheme = localStorage.getItem("techo_theme");
if (savedTheme === "dark" || savedTheme === "light") {
  htmlTag.setAttribute("data-theme", savedTheme);
  if (btnTheme) {
    btnTheme.textContent = savedTheme === "dark" ? "🌙" : "☀";
  }
} else {
  // por defecto: light
  htmlTag.setAttribute("data-theme", "light");
  if (btnTheme) {
    btnTheme.textContent = "☀";
  }
}

// Cargar escala de fuente guardada
const savedFontScale = localStorage.getItem("techo_font_scale");
if (savedFontScale) {
  document.documentElement.style.setProperty("--font-scale", savedFontScale);
}

// ====== Toggle tema claro/oscuro ======
if (btnTheme) {
  btnTheme.addEventListener("click", () => {
    const current = htmlTag.getAttribute("data-theme");
    const next = current === "light" ? "dark" : "light";

    htmlTag.setAttribute("data-theme", next);
    localStorage.setItem("techo_theme", next);

    btnTheme.textContent = next === "dark" ? "🌙" : "☀";
  });
}

// ====== Accesibilidad: tamaño de letra ======
function setFontScale(scale) {
  document.documentElement.style.setProperty("--font-scale", scale);
  localStorage.setItem("techo_font_scale", scale);
}

// Aumentar letra
if (btnFontPlus) {
  btnFontPlus.addEventListener("click", () => {
    // leer valor actual
    const current = parseFloat(
      getComputedStyle(document.documentElement)
        .getPropertyValue("--font-scale")
    ) || 1;

    const next = Math.min(current + 0.1, 1.4); // máx 140%
    setFontScale(next.toFixed(2));
  });
}

// Disminuir / volver estándar
if (btnFontMinus) {
  btnFontMinus.addEventListener("click", () => {
    const current = parseFloat(
      getComputedStyle(document.documentElement)
        .getPropertyValue("--font-scale")
    ) || 1;

    const next = Math.max(current - 0.1, 1.0); // mín 100%
    setFontScale(next.toFixed(2));
  });
}

console.log("Landing JS activo: tema y accesibilidad listos.");
