from django.shortcuts import render, redirect, get_object_or_404
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
from django.utils import timezone

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
    
    # Verificar que el usuario existe y está autenticado
    if not user or not user.is_authenticated:
        return redirect("login")
    
    perfil, _ = PerfilUsuario.objects.get_or_create(user=user)
    if user.is_superuser and perfil.rol != "Admin":
        perfil.rol = "Admin"; perfil.save()
    if not perfil.rol:
        perfil.rol = "Trabajador"; perfil.save()

    rol = perfil.rol
    
    # Determinar nombre de usuario de forma segura
    nombre_usuario = perfil.nombre if perfil.nombre else (user.username if hasattr(user, 'username') else "Usuario")
    
    ctx = {
        "rol": rol, 
        "mensaje": "", 
        "proyectos": [], 
        "viviendas": [], 
        "registros": [], 
        "actividad": [],
        "usuario": user,
        "perfil": perfil,
        "nombre_usuario": nombre_usuario,
        "user": user,  # Agregar user también
    }

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
            ctx["proyecto_asignado"] = p
            ctx["proyectos"] = [p]
            ctx["viviendas"] = Vivienda.objects.filter(proyecto=p)[:200]
            ctx["registros"] = RegistroPostventa.objects.filter(proyecto=p).select_related('reportante').order_by("-creado_en")[:20]
        else:
            ctx["proyecto_asignado"] = None
            ctx["mensaje"] = "Aún no tienes un proyecto asignado."
        return render(request, "accounts/dashboard_trabajador.html", ctx)
    
    elif rol == "Familia":
        v = perfil.vivienda_asignada
        if v:
            ctx["vivienda"] = v
            ctx["proyecto"] = v.proyecto
            ctx["proyectos"] = [v.proyecto]
            ctx["viviendas"] = [v]
            # Obtener observaciones reportadas por este usuario
            observaciones = RegistroPostventa.objects.filter(
                reportante=user
            ).select_related('proyecto').prefetch_related('evidencia_set').order_by("-creado_en")[:50]
            ctx["observaciones"] = observaciones
            ctx["registros"] = observaciones  # Para compatibilidad con templates existentes
        else:
            ctx["vivienda"] = None
            ctx["proyecto"] = None
            ctx["observaciones"] = []
            ctx["mensaje"] = "Tu vivienda aún no ha sido vinculada."
        return render(request, "accounts/dashboard_familia.html", ctx)
    
    # Fallback al dashboard genérico si no hay rol definido
    return render(request, "accounts/dashboard.html", ctx)

@login_required
def perfil(request):
    perfil = request.user.perfil
    es_primera_vez = not perfil.rut or not perfil.nombre or not perfil.apellido
    
    if request.method == "POST":
        form = PerfilForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            # Si no es la primera vez, no permitir cambiar RUT, nombre, apellido, fecha_nacimiento
            if not es_primera_vez:
                form.instance.rut = perfil.rut
                form.instance.nombre = perfil.nombre
                form.instance.apellido = perfil.apellido
                form.instance.fecha_nacimiento = perfil.fecha_nacimiento
            
            form.save()
            messages.success(request, "✅ Perfil actualizado correctamente")
            return redirect("perfil")
    else:
        form = PerfilForm(instance=perfil)
        
        # Deshabilitar campos si ya tienen valor
        if perfil.rut:
            form.fields['rut'].widget.attrs['readonly'] = 'readonly'
            form.fields['rut'].widget.attrs['class'] += ' bg-light'
            form.fields['rut'].help_text = "⚠️ El RUT no se puede modificar una vez establecido"
        
        if perfil.nombre:
            form.fields['nombre'].widget.attrs['readonly'] = 'readonly'
            form.fields['nombre'].widget.attrs['class'] += ' bg-light'
        
        if perfil.apellido:
            form.fields['apellido'].widget.attrs['readonly'] = 'readonly'
            form.fields['apellido'].widget.attrs['class'] += ' bg-light'
        
        if perfil.fecha_nacimiento:
            form.fields['fecha_nacimiento'].widget.attrs['readonly'] = 'readonly'
            form.fields['fecha_nacimiento'].widget.attrs['class'] += ' bg-light'
    
    return render(request, "accounts/perfil.html", {
        "form": form,
        "rol": perfil.rol,
        "es_primera_vez": es_primera_vez
    })

@login_required
def ayuda(request):
    perfil = request.user.perfil
    sent = False
    if request.method == "POST":
        form = AyudaForm(request.POST, request.FILES)
        if form.is_valid():
            asunto_usuario = form.cleaned_data["asunto"]
            mensaje_usuario = form.cleaned_data["mensaje"]
            
            # Información del usuario
            nombre_completo = f"{request.user.first_name} {request.user.last_name}"
            correo = request.user.email
            rol = perfil.rol
            telefono = perfil.telefono or "No proporcionado"
            
            # Construir mensaje HTML profesional
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #0073e6 0%, #005bb5 100%); color: white; padding: 30px; text-align: center; border-radius: 8px 8px 0 0; }}
                    .content {{ background: #f8f9fa; padding: 30px; border: 1px solid #e0e0e0; }}
                    .info-box {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #0073e6; }}
                    .info-row {{ display: flex; margin-bottom: 10px; }}
                    .info-label {{ font-weight: bold; min-width: 120px; color: #666; }}
                    .info-value {{ color: #333; }}
                    .message-box {{ background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0; margin-top: 20px; }}
                    .footer {{ background: #f1f1f1; padding: 20px; text-align: center; font-size: 12px; color: #666; border-radius: 0 0 8px 8px; }}
                    .badge {{ display: inline-block; padding: 5px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
                    .badge-admin {{ background: #dc3545; color: white; }}
                    .badge-trabajador {{ background: #17a2b8; color: white; }}
                    .badge-familia {{ background: #ffc107; color: black; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1 style="margin: 0; font-size: 24px;">📧 Solicitud de Ayuda</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">Plataforma de Gestión de Viviendas</p>
                    </div>
                    
                    <div class="content">
                        <div class="info-box">
                            <h2 style="margin-top: 0; color: #0073e6; font-size: 18px;">👤 Información del Usuario</h2>
                            <div class="info-row">
                                <span class="info-label">Nombre:</span>
                                <span class="info-value">{nombre_completo}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Correo:</span>
                                <span class="info-value">{correo}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Teléfono:</span>
                                <span class="info-value">{telefono}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Rol:</span>
                                <span class="info-value">
                                    <span class="badge badge-{rol.lower()}">{rol}</span>
                                </span>
                            </div>
                        </div>
                        
                        <div class="info-box">
                            <h2 style="margin-top: 0; color: #0073e6; font-size: 18px;">📋 Asunto</h2>
                            <p style="margin: 0; font-size: 16px; font-weight: bold;">{asunto_usuario}</p>
                        </div>
                        
                        <div class="message-box">
                            <h3 style="margin-top: 0; color: #666; font-size: 14px;">💬 Mensaje:</h3>
                            <p style="white-space: pre-wrap; margin: 0;">{mensaje_usuario}</p>
                        </div>
                        
                        <p style="margin-top: 20px; padding: 15px; background: #e3f2fd; border-radius: 4px; font-size: 13px;">
                            <strong>⏰ Fecha de solicitud:</strong> {timezone.localtime().strftime('%d/%m/%Y %H:%M:%S')}
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p style="margin: 0;">TECHO Chile - Plataforma de Recepción y Postventa Habitacional</p>
                        <p style="margin: 5px 0 0 0;">Este es un correo automático generado por el sistema</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Enviar email con HTML
            from django.core.mail import EmailMultiAlternatives
            from django.utils import timezone
            
            asunto_email = f"[TECHO] Solicitud de Ayuda: {asunto_usuario}"
            
            email = EmailMultiAlternatives(
                subject=asunto_email,
                body=f"De: {nombre_completo} ({correo})\nRol: {rol}\n\nAsunto: {asunto_usuario}\n\n{mensaje_usuario}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=["proyecto.techochile@gmail.com"],
                reply_to=[correo]
            )
            email.attach_alternative(html_message, "text/html")
            
            # Adjuntar evidencia si existe
            evidencia = form.cleaned_data.get("evidencia")
            if evidencia:
                email.attach(evidencia.name, evidencia.read(), evidencia.content_type)
            
            try:
                email.send(fail_silently=False)
                sent = True
                messages.success(request, f"✅ Tu mensaje ha sido enviado exitosamente. Te contactaremos pronto a {correo}")
            except Exception as e:
                messages.error(request, f"❌ Error al enviar el mensaje: {str(e)}")
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
        rut = request.POST.get("rut", "").strip()
        fecha_nacimiento = request.POST.get("fecha_nacimiento", "").strip()
        nacionalidad = request.POST.get("nacionalidad", "").strip() or "Chilena"
        telefono = request.POST.get("telefono", "").strip()
        telefono_secundario = request.POST.get("telefono_secundario", "").strip()
        direccion = request.POST.get("direccion", "").strip()
        ciudad = request.POST.get("ciudad", "").strip()
        comuna = request.POST.get("comuna", "").strip()
        region = request.POST.get("region", "").strip()
        contacto_emergencia_nombre = request.POST.get("contacto_emergencia_nombre", "").strip()
        contacto_emergencia_telefono = request.POST.get("contacto_emergencia_telefono", "").strip()
        contacto_emergencia_relacion = request.POST.get("contacto_emergencia_relacion", "").strip()
        rol = request.POST.get("rol", "")
        password = request.POST.get("password", "")
        proyecto_id = request.POST.get("proyecto_id")
        vivienda_id = request.POST.get("vivienda_id")
        
        # Validaciones
        if not all([correo, nombre, apellido, rut, telefono, rol, password]):
            messages.error(request, "Todos los campos obligatorios deben estar completos (correo, nombre, apellido, RUT, teléfono, rol, contraseña)")
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
                    perfil_nuevo.rut = rut
                    perfil_nuevo.fecha_nacimiento = fecha_nacimiento if fecha_nacimiento else None
                    perfil_nuevo.nacionalidad = nacionalidad
                    perfil_nuevo.telefono = telefono
                    perfil_nuevo.telefono_secundario = telefono_secundario
                    perfil_nuevo.correo_personal = correo
                    perfil_nuevo.direccion = direccion
                    perfil_nuevo.ciudad = ciudad
                    perfil_nuevo.comuna = comuna
                    perfil_nuevo.region = region
                    perfil_nuevo.contacto_emergencia_nombre = contacto_emergencia_nombre
                    perfil_nuevo.contacto_emergencia_telefono = contacto_emergencia_telefono
                    perfil_nuevo.contacto_emergencia_relacion = contacto_emergencia_relacion
                    
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


@login_required
def listar_usuarios(request):
    """Vista para listar todos los usuarios del sistema"""
    perfil = request.user.perfil
    
    # Solo Admin puede acceder
    if perfil.rol != "Admin":
        messages.error(request, "No tienes permisos para acceder a esta página")
        return redirect("dashboard")
    
    # Obtener todos los usuarios con sus perfiles
    usuarios = User.objects.select_related('perfil').all().order_by('-date_joined')
    
    # Calcular contadores por rol
    total_admin = usuarios.filter(perfil__rol='Admin').count()
    total_trabajadores = usuarios.filter(perfil__rol='Trabajador').count()
    total_familias = usuarios.filter(perfil__rol='Familia').count()
    
    ctx = {
        "rol": perfil.rol,
        "usuarios": usuarios,
        "total_admin": total_admin,
        "total_trabajadores": total_trabajadores,
        "total_familias": total_familias,
    }
    
    return render(request, "accounts/listar_usuarios.html", ctx)


@login_required
def editar_usuario(request, user_id):
    """Vista para editar un usuario existente"""
    perfil = request.user.perfil
    
    # Solo Admin puede acceder
    if perfil.rol != "Admin":
        messages.error(request, "No tienes permisos para acceder a esta página")
        return redirect("dashboard")
    
    usuario = get_object_or_404(User, id=user_id)
    perfil_usuario = usuario.perfil
    
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        apellido = request.POST.get("apellido", "").strip()
        correo = request.POST.get("correo", "").strip()
        rol = request.POST.get("rol", "")
        proyecto_id = request.POST.get("proyecto_id")
        vivienda_id = request.POST.get("vivienda_id")
        telefono = request.POST.get("telefono", "").strip()
        nueva_password = request.POST.get("nueva_password", "").strip()
        
        # Validaciones
        if not all([nombre, apellido, correo, rol]):
            messages.error(request, "Los campos nombre, apellido, correo y rol son obligatorios")
        elif rol not in ["Trabajador", "Familia", "Admin"]:
            messages.error(request, "Rol inválido")
        else:
            try:
                # Actualizar User
                usuario.first_name = nombre
                usuario.last_name = apellido
                usuario.email = correo
                
                # Cambiar contraseña si se proporcionó una nueva
                if nueva_password:
                    usuario.set_password(nueva_password)
                    messages.success(request, "Contraseña actualizada exitosamente")
                
                # Actualizar is_superuser basado en el rol
                if rol == "Admin":
                    usuario.is_superuser = True
                    usuario.is_staff = True
                else:
                    usuario.is_superuser = False
                    usuario.is_staff = False
                
                usuario.save()
                
                # Actualizar PerfilUsuario
                perfil_usuario.nombre = nombre
                perfil_usuario.apellido = apellido
                perfil_usuario.correo_personal = correo
                perfil_usuario.rol = rol
                perfil_usuario.telefono = telefono
                
                # Asignar proyecto si es Trabajador
                if rol == "Trabajador" and proyecto_id:
                    try:
                        proyecto = Proyecto.objects.get(id=proyecto_id)
                        perfil_usuario.proyecto_asignado = proyecto
                    except Proyecto.DoesNotExist:
                        perfil_usuario.proyecto_asignado = None
                else:
                    perfil_usuario.proyecto_asignado = None
                
                # Asignar vivienda si es Familia
                if rol == "Familia" and vivienda_id:
                    try:
                        vivienda = Vivienda.objects.get(id=vivienda_id)
                        perfil_usuario.vivienda_asignada = vivienda
                    except Vivienda.DoesNotExist:
                        perfil_usuario.vivienda_asignada = None
                else:
                    perfil_usuario.vivienda_asignada = None
                
                perfil_usuario.save()
                
                messages.success(request, f"Usuario {correo} actualizado exitosamente")
                return redirect("listar_usuarios")
                
            except Exception as e:
                messages.error(request, f"Error al actualizar usuario: {str(e)}")
    
    # Obtener proyectos y viviendas para los selectores
    proyectos = Proyecto.objects.all().order_by("codigo")
    viviendas = Vivienda.objects.select_related("proyecto").all().order_by("proyecto__codigo")
    
    ctx = {
        "rol": perfil.rol,
        "usuario_editar": usuario,
        "perfil_editar": perfil_usuario,
        "proyectos": proyectos,
        "viviendas": viviendas
    }
    
    return render(request, "accounts/editar_usuario.html", ctx)


@login_required
def eliminar_usuario(request, user_id):
    """Vista para eliminar un usuario con confirmación de seguridad"""
    perfil = request.user.perfil
    
    # Solo Admin puede acceder
    if perfil.rol != "Admin":
        messages.error(request, "No tienes permisos para acceder a esta página")
        return redirect("dashboard")
    
    usuario = get_object_or_404(User, id=user_id)
    
    # No permitir que se elimine a sí mismo
    if usuario == request.user:
        messages.error(request, "No puedes eliminar tu propio usuario")
        return redirect("listar_usuarios")
    
    if request.method == "POST":
        # Verificar texto de confirmación
        confirmacion = request.POST.get('confirmacion', '').strip()
        texto_esperado = "acepto eliminar usuario"
        
        if confirmacion.lower() != texto_esperado:
            messages.error(request, 
                f"⚠️ Debes escribir exactamente: '{texto_esperado}' para confirmar la eliminación")
            return redirect("listar_usuarios")
        
        nombre_completo = f"{usuario.first_name} {usuario.last_name}"
        correo = usuario.username
        usuario.delete()
        messages.success(request, f"Usuario {nombre_completo} ({correo}) eliminado exitosamente")
        return redirect("listar_usuarios")
    
    ctx = {
        "rol": perfil.rol,
        "usuario_eliminar": usuario
    }
    
    return render(request, "accounts/eliminar_usuario.html", ctx)


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
        
        # Verificar si el email está configurado en producción
        email_configurado = settings.EMAIL_BACKEND != 'django.core.mail.backends.console.EmailBackend'
        
        if email_configurado:
            try:
                # Intentar enviar email con timeout corto para evitar WORKER TIMEOUT
                from django.core.mail import get_connection
                
                connection = get_connection(
                    backend=settings.EMAIL_BACKEND,
                    host=settings.EMAIL_HOST,
                    port=settings.EMAIL_PORT,
                    username=settings.EMAIL_HOST_USER,
                    password=settings.EMAIL_HOST_PASSWORD,
                    use_tls=settings.EMAIL_USE_TLS,
                    timeout=10  # Timeout de 10 segundos
                )
                
                send_mail(
                    subject=asunto,
                    message=mensaje,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[correo],
                    fail_silently=False,
                    connection=connection,
                )
                messages.success(request, 
                    f"✅ Se ha enviado un código de recuperación a {correo}. Revisa tu bandeja de entrada.")
                return redirect("recuperar_password_verificar")
            
            except Exception as e:
                # Registrar error en logs pero NUNCA mostrar el código
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error enviando email de recuperación: {e}")
                
                # CRÍTICO: NUNCA mostrar el código en pantalla por seguridad
                # Marcar el token como no usado para que el admin pueda ayudar
                TokenRecuperacion.objects.filter(token=codigo).update(usado=False)
                
                messages.error(request, 
                    "⚠️ Hubo un problema al enviar el correo. Por favor, contacta con soporte o intenta nuevamente más tarde.")
                return redirect("recuperar_password_solicitar")
        else:
            # Modo desarrollo: solo mostrar en consola del servidor, NUNCA en la vista
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Email no configurado. Código para {correo}: {codigo}")
            
            messages.error(request, 
                "⚠️ El sistema de correos no está configurado. Contacta con el administrador.")
            return redirect("recuperar_password_solicitar")
    
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