const API_URL = "http://127.0.0.1:8000/api";

async function getCurrentUser() {
  const token = localStorage.getItem("jwt");
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  const res = await fetch(`${API_URL}/me/`, {
    method: "GET",
    headers: {
      Authorization: "Bearer " + token
    }
  });

  if (!res.ok) {
    // token malo o expirado
    localStorage.removeItem("jwt");
    localStorage.removeItem("role");
    localStorage.removeItem("user_email");
    window.location.href = "login.html";
    return;
  }

  const data = await res.json();
  return data;
}

function logout() {
  localStorage.removeItem("jwt");
  localStorage.removeItem("role");
  localStorage.removeItem("user_email");
  window.location.href = "login.html";
}
