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
        # Actividad reciente (últimas evidencias y cambios)
        ev = Evidencia.objects.select_related("registro","subido_por").order_by("-creado_en")[:10]
        ctx["actividad"] = ev
        return render(request, "accounts/dashboard_admin.html", ctx)
    
    elif rol == "Trabajador":
        p = perfil.proyecto_asignado
        if p:
            ctx["proyectos"] = [p]
            ctx["viviendas"] = Vivienda.objects.filter(proyecto=p)[:200]
            ctx["registros"] = RegistroPostventa.objects.filter(proyecto=p).order_by("-creado_en")[:20]
        else:
            ctx["mensaje"] = "Aún no tienes un proyecto asignado."
        return render(request, "accounts/dashboard_trabajador.html", ctx)
    
    elif rol == "Familia":
        v = perfil.vivienda_asignada
        if v:
            ctx["proyectos"] = [v.proyecto]
            ctx["viviendas"] = [v]
            ctx["registros"] = RegistroPostventa.objects.filter(ficha__vivienda=v).order_by("-creado_en")[:20]
        else:
            ctx["mensaje"] = "Tu vivienda aún no ha sido vinculada."
        return render(request, "accounts/dashboard_familia.html", ctx)
    
    # Fallback al dashboard genérico si no hay rol definido
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

@login_required
def crear_usuario(request):
    """Vista para que Admin cree usuarios (Trabajadores o Familias)"""
    perfil = request.user.perfil
    
    # Solo Admin puede acceder
    if perfil.rol != "Admin":
        messages.error(request, "No tienes permisos para acceder a esta página")
        return redirect("dashboard")
    
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip()
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        rol = request.POST.get("rol", "")
        password = request.POST.get("password", "")
        proyecto_id = request.POST.get("proyecto_id")
        vivienda_id = request.POST.get("vivienda_id")
        
        # Validaciones
        if not all([correo, nombre, apellido, rol, password]):
            messages.error(request, "Todos los campos obligatorios deben estar completos")
        elif rol not in ["Trabajador", "Familia", "Admin"]:
            messages.error(request, "Rol inválido")
        else:
            # Verificar si el usuario ya existe
            from django.contrib.auth.models import User
            if User.objects.filter(username=correo).exists():
                messages.error(request, f"Ya existe un usuario con el correo {correo}")
            else:
                try:
                    # Si es Admin, crear como superuser desde el inicio
                    if rol == "Admin":
                        user = User.objects.create_superuser(
                            username=correo,
                            email=correo,
                            password=password,
                            first_name=nombre,
                            last_name=apellido
                        )
                    else:
                        # Crear usuario normal
                        user = User.objects.create_user(
                            username=correo,
                            email=correo,
                            password=password,
                            first_name=nombre,
                            last_name=apellido
                        )
                    
                    # Obtener el perfil creado automáticamente por el signal
                    perfil_nuevo = PerfilUsuario.objects.get(user=user)
                    
                    # Actualizar el rol correcto (si no es Admin, porque el signal ya lo asigna correctamente)
                    if rol != "Admin" and perfil_nuevo.rol != rol:
                        perfil_nuevo.rol = rol
                    
                    # Actualizar información adicional del perfil
                    perfil_nuevo.nombre = nombre
                    perfil_nuevo.apellido = apellido
                    perfil_nuevo.correo_personal = correo
                    
                    # Asignar proyecto si es Trabajador
                    if rol == "Trabajador" and proyecto_id:
                        try:
                            proyecto = Proyecto.objects.get(id=proyecto_id)
                            perfil_nuevo.proyecto_asignado = proyecto
                        except Proyecto.DoesNotExist:
                            messages.warning(request, "Proyecto no encontrado, pero el usuario fue creado")
                    
                    # Asignar vivienda si es Familia
                    elif rol == "Familia" and vivienda_id:
                        try:
                            vivienda = Vivienda.objects.get(id=vivienda_id)
                            perfil_nuevo.vivienda_asignada = vivienda
                        except Vivienda.DoesNotExist:
                            messages.warning(request, "Vivienda no encontrada, pero el usuario fue creado")
                    
                    # Guardar el perfil con todos los cambios
                    perfil_nuevo.save()
                    
                    messages.success(request, f"Usuario {correo} creado exitosamente como {rol}")
                    return redirect("crear_usuario")
                    
                except Exception as e:
                    messages.error(request, f"Error al crear usuario: {str(e)}")
    
    # Obtener proyectos y viviendas para los selectores
    proyectos = Proyecto.objects.all().order_by("codigo")
    viviendas = Vivienda.objects.select_related("proyecto").all().order_by("proyecto__codigo")
    
    ctx = {
        "rol": perfil.rol,
        "proyectos": proyectos,
        "viviendas": viviendas
    }
    
    return render(request, "accounts/crear_usuario.html", ctx)