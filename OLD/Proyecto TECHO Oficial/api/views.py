from django.shortcuts import render, redirect
from django.http import HttpRequest, HttpResponse
from django.contrib import messages
from .models import PlataformaUser

# Landing pública
def landing_view(request: HttpRequest) -> HttpResponse:
    return render(request, "landing.html")

# Dashboard Admin
def dashboard_admin(request: HttpRequest) -> HttpResponse:
    # seguridad mínima: si no está logeado o no es admin → devuélvelo a login
    user_id = request.session.get("user_id")
    user_rol = request.session.get("user_rol")

    if not user_id or user_rol != "ADMIN":
        return redirect("login")

    user = PlataformaUser.objects.get(id=user_id)
    context = {
        "user": user,
        "panel_title": "Panel Administración",
    }
    return render(request, "panel_admin.html", context)


# Dashboard Trabajador
def dashboard_trabajador(request: HttpRequest) -> HttpResponse:
    user_id = request.session.get("user_id")
    user_rol = request.session.get("user_rol")

    if not user_id or user_rol != "TRABAJADOR":
        return redirect("login")

    user = PlataformaUser.objects.get(id=user_id)
    context = {
        "user": user,
        "panel_title": "Panel Trabajador",
    }
    return render(request, "panel_trabajador.html", context)


# Dashboard Familia
def dashboard_familia(request: HttpRequest) -> HttpResponse:
    user_id = request.session.get("user_id")
    user_rol = request.session.get("user_rol")

    if not user_id or user_rol != "FAMILIA":
        return redirect("login")

    user = PlataformaUser.objects.get(id=user_id)
    context = {
        "user": user,
        "panel_title": "Mi Vivienda",
    }
    return render(request, "dashboard_familia.html", context)


# ---------- LOGIN ----------
def login_view(request: HttpRequest) -> HttpResponse:
    """
    Pantalla de login + lógica de autenticación manual
    """

    # Si el usuario ya está en sesión, mándalo directo a su dashboard
    if request.session.get("user_id") and request.session.get("user_rol"):
        return _redirect_by_role(request.session["user_rol"])

    if request.method == "POST":
        correo = request.POST.get("correo", "").strip().lower()
        password = request.POST.get("password", "").strip()

        # Validaciones básicas
        if correo == "" or password == "":
            messages.error(request, "Debes ingresar correo y contraseña.")
            return render(request, "login.html")

        try:
            # buscamos al usuario
            u = PlataformaUser.objects.get(correo__iexact=correo)
        except PlataformaUser.DoesNotExist:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "login.html")

        # Comparamos con la contraseña simple (password_plana, por ahora)
        if u.password_plana != password:
            messages.error(request, "Correo o contraseña incorrectos.")
            return render(request, "login.html")

        # Si ok → guardamos sesión
        request.session["user_id"] = u.id
        request.session["user_rol"] = u.rol
        request.session["user_nombre"] = u.nombre

        # Redirigir según rol
        return _redirect_by_role(u.rol)

    # GET normal → cargar template vacío
    return render(request, "login.html")


def _redirect_by_role(rol: str) -> HttpResponse:
    """
    Función interna: según el rol, manda a la vista correcta
    """
    if rol == "ADMIN":
        return redirect("dashboard_admin")
    elif rol == "TRABAJADOR":
        return redirect("dashboard_trabajador")
    elif rol == "FAMILIA":
        return redirect("dashboard_familia")
    else:
        # fallback raro
        return redirect("landing")


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Cerrar sesión.
    """
    request.session.flush()  # mata toda la sesión
    return redirect("login")


