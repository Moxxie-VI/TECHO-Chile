from django.shortcuts import render, redirect
from api.views_auth import get_user_from_session
from api.models import Trabajador

def view_landing(request):
    return render(request, "landing.html")

def view_login(request):
    # si YA está logeado, no tiene que ver el login de nuevo
    user = get_user_from_session(request)
    if user:
        if user["role"] == "ADMIN":
            return redirect("/panel/admin/")
        else:
            return redirect("/panel/trabajador/")
    return render(request, "login.html")

def view_recuperar(request):
    return render(request, "recuperar.html")

def view_panel_trabajador(request):
    user = get_user_from_session(request)
    if not user:
        return redirect("/login/")
    if user["role"] not in ["TECHO", "ADMIN"]:
        return redirect("/login/")

    trabajador = Trabajador.objects.filter(id=user["id"]).first()

    ctx = {
        "email": user["email"],
        "role": user["role"],
        "nombre": trabajador.nombreTrab if trabajador else "",
        "apellido": trabajador.apellidoTrab if trabajador else "",
    }
    return render(request, "panel_trabajador.html", ctx)



def view_panel_admin(request):
    user = get_user_from_session(request)
    if not user:
        return redirect("/login/")
    if user["role"] != "ADMIN":
        return redirect("/panel/trabajador/")

    trabajador = Trabajador.objects.filter(id=user["id"]).first()

    ctx = {
        "email": user["email"],
        "role": user["role"],
        "nombre": trabajador.nombreTrab if trabajador else "",
        "apellido": trabajador.apellidoTrab if trabajador else "",
        "avatar_url": getattr(trabajador, "avatar_url", ""),  # si después guardas foto
    }
    return render(request, "panel_admin.html", ctx)




