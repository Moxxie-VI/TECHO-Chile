from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from core.models import Privilegio
from core.models import PerfilUsuario, Proyecto, Vivienda, RegistroPostventa, Evidencia
from django.core.mail import EmailMessage, send_mail
from core.forms import PerfilForm, AyudaForm
from .models import TokenRecuperacion
from django.conf import settings

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


# ============================================================================
# RECUPERACIÓN DE CONTRASEÑA
# ============================================================================

def recuperar_password_solicitar(request):
    """
    Vista para solicitar recuperación de contraseña
    El usuario ingresa su correo y se le envía un código
    """
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        correo = request.POST.get("correo", "").strip()
        
        # Validar que el correo no esté vacío
        if not correo:
            messages.error(request, "Por favor ingresa tu correo electrónico")
            return render(request, "accounts/recuperar_password_solicitar.html")
        
        # Buscar usuario por correo (username = correo en este sistema)
        try:
            user = User.objects.get(username=correo)
        except User.DoesNotExist:
            # Por seguridad, no revelamos si el correo existe o no
            messages.success(request, 
                f"Si el correo {correo} está registrado, recibirás un código de recuperación en los próximos minutos.")
            return redirect("login")
        
        # Generar token único
        codigo = TokenRecuperacion.generar_codigo()
        
        # Guardar en base de datos
        TokenRecuperacion.objects.create(
            user=user,
            token=codigo
        )
        
        # Enviar correo con el código
        asunto = "Código de Recuperación de Contraseña - TECHO Chile"
        
        mensaje = f"""
Hola {user.first_name or user.username},

Has solicitado recuperar tu contraseña en la Plataforma de Gestión de Viviendas de TECHO Chile.

Tu código de recuperación es:

    {codigo}

Este código es válido por 15 minutos.

Para restablecer tu contraseña:
1. Ingresa a la página de recuperación
2. Introduce este código
3. Establece tu nueva contraseña

Si no solicitaste este cambio, ignora este correo.

---
TECHO Chile
Plataforma de Recepción y Postventa Habitacional

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Este es un correo automático, por favor no respondas.
        """
        
        try:
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[correo],
                fail_silently=False,
            )
            messages.success(request, 
                f"Se ha enviado un código de recuperación a {correo}. Revisa tu bandeja de entrada.")
            return redirect("recuperar_password_verificar")
        
        except Exception as e:
            messages.error(request, 
                f"Error al enviar el correo. Por favor intenta más tarde. (Error: {str(e)})")
            return render(request, "accounts/recuperar_password_solicitar.html")
    
    return render(request, "accounts/recuperar_password_solicitar.html")


def recuperar_password_verificar(request):
    """
    Vista para verificar el código y cambiar la contraseña
    """
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        codigo = request.POST.get("codigo", "").strip().upper()
        nueva_password = request.POST.get("nueva_password", "")
        confirmar_password = request.POST.get("confirmar_password", "")
        
        # Validaciones
        if not codigo:
            messages.error(request, "Por favor ingresa el código de recuperación")
            return render(request, "accounts/recuperar_password_verificar.html")
        
        if not nueva_password or not confirmar_password:
            messages.error(request, "Por favor completa ambos campos de contraseña")
            return render(request, "accounts/recuperar_password_verificar.html")
        
        if nueva_password != confirmar_password:
            messages.error(request, "Las contraseñas no coinciden")
            return render(request, "accounts/recuperar_password_verificar.html")
        
        if len(nueva_password) < 6:
            messages.error(request, "La contraseña debe tener al menos 6 caracteres")
            return render(request, "accounts/recuperar_password_verificar.html")
        
        # Buscar token
        try:
            token = TokenRecuperacion.objects.get(token=codigo, usado=False)
        except TokenRecuperacion.DoesNotExist:
            messages.error(request, "Código inválido o ya utilizado")
            return render(request, "accounts/recuperar_password_verificar.html")
        
        # Verificar que el token sea válido (no expirado)
        if not token.es_valido():
            messages.error(request, "El código ha expirado. Solicita uno nuevo.")
            return redirect("recuperar_password_solicitar")
        
        # Cambiar contraseña
        user = token.user
        user.set_password(nueva_password)
        user.save()
        
        # Marcar token como usado
        token.usado = True
        token.save()
        
        messages.success(request, 
            "✅ Tu contraseña ha sido actualizada exitosamente. Ya puedes iniciar sesión.")
        return redirect("login")
    
    return render(request, "accounts/recuperar_password_verificar.html")