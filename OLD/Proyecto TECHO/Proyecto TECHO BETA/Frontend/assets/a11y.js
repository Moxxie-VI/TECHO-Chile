const a11yBtn = document.getElementById("a11y-toggle");
const root = document.documentElement; // <html>

// lee preferencia guardada
const savedA11y = localStorage.getItem("a11y") === "on";

if (savedA11y) {
  root.classList.add("a11y-highcontrast");
}

if (a11yBtn) {
  a11yBtn.addEventListener("click", () => {
    const active = root.classList.toggle("a11y-highcontrast");
    localStorage.setItem("a11y", active ? "on" : "off");
  });
}
