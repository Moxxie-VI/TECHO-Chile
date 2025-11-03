from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from core.models import Privilegio
from core.models import PerfilUsuario, Proyecto, Vivienda, RegistroPostventa, Evidencia
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from core.forms import PerfilForm, AyudaForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        correo = request.POST.get("correo")
        clave = request.POST.get("clave")
        user = authenticate(request, username=correo, password=clave)
        if user:
            login(request, user)
            return redirect("dashboard")
        messages.error(request, "Credenciales inválidas")
    return render(request, "accounts/login.html")

def logout_view(request):
    logout(request)
    return redirect("home")



@login_required
def dashboard(request):
    user = request.user
    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    if user.is_superuser and perfil.rol != "Admin":
        perfil.rol = "Admin"; perfil.save()
    if not perfil.rol:
        perfil.rol = "Trabajador"; perfil.save()

    rol = perfil.rol
    ctx = {"rol": rol, "mensaje": "", "proyectos": [], "viviendas": [], "registros": [], "actividad": []}

    if rol == "Admin":
        ctx["proyectos"] = Proyecto.objects.all().order_by("codigo")[:200]
        ctx["viviendas"] = Vivienda.objects.select_related("proyecto").all()[:200]
        ctx["registros"] = RegistroPostventa.objects.select_related("proyecto").order_by("-creado_en")[:20]
    elif rol == "Trabajador":
        p = perfil.proyecto_asignado
        if p:
            ctx["proyectos"] = [p]
            ctx["viviendas"] = Vivienda.objects.filter(proyecto=p)[:200]
            ctx["registros"] = RegistroPostventa.objects.filter(proyecto=p).order_by("-creado_en")[:20]
        else:
            ctx["mensaje"] = "Aún no tienes un proyecto asignado."
    elif rol == "Familia":
        v = perfil.vivienda_asignada
        if v:
            ctx["proyectos"] = [v.proyecto]
            ctx["viviendas"] = [v]
            ctx["registros"] = RegistroPostventa.objects.filter(ficha__vivienda=v).order_by("-creado_en")[:20]
        else:
            ctx["mensaje"] = "Tu vivienda aún no ha sido vinculada."

    # Actividad reciente (últimas evidencias y cambios)
    ev = Evidencia.objects.select_related("registro","subido_por").order_by("-creado_en")[:10]
    ctx["actividad"] = ev
    return render(request, "accounts/dashboard.html", ctx)

@login_required
def perfil(request):
    perfil = request.user.perfil
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            form.save()
    else:
        form = PerfilForm(instance=perfil)
    return render(request, "accounts/perfil.html", {"form": form, "rol": perfil.rol})

@login_required
def ayuda(request):
    perfil = request.user.perfil
    sent = False
    if request.method == "POST":
        form = AyudaForm(request.POST)
        if form.is_valid():
            msg = form.cleaned_data["mensaje"]
            asunto = f"[TECHO] {form.cleaned_data['asunto']}"
            body = f"De: {request.user.username}\nRol: {perfil.rol}\n\n{msg}"
            email = EmailMessage(subject=asunto, body=body, to=["soporte@techo.cl"])
            email.send(fail_silently=False)
            sent = True
    else:
        form = AyudaForm()
    return render(request, "accounts/ayuda.html", {"form": form, "enviado": sent, "rol": perfil.rol})

@login_required
def tutorial(request):
    return render(request, "accounts/tutorial.html", {"rol": request.user.perfil.rol})