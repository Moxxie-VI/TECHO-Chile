const API_URL = "http://127.0.0.1:8000/api";

const loginForm = document.getElementById("loginForm");

loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value.trim();

  // llamada al backend
  const res = await fetch(`${API_URL}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });

  const data = await res.json();

  if (!res.ok) {
    alert(data.detail || "Credenciales inválidas");
    return;
  }

  // Guardar sesión local
  localStorage.setItem("jwt", data.access);       // token para futuras llamadas
  localStorage.setItem("role", data.role);        // ADMIN / TECHO / FAMILIA
  localStorage.setItem("user_email", data.email); // para mostrar "Hola, ..."

  // Redirección según el rol
  if (data.role === "ADMIN") {
    window.location.href = "dashboard_admin.html";
  } else if (data.role === "TECHO") {
    window.location.href = "dashboard_techo.html";
  } else {
    window.location.href = "mi_vivienda.html";
  }
});
