from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import require_role
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import EmailMessage
from django.db.models import Count, Q
from .forms import ProyectoForm, ViviendaForm, RegistroPostventaForm, EvidenciaForm
from .models import Proyecto, Vivienda, RegistroPostventa, Evidencia, ESTADOS, FichaInmueble, PerfilUsuario
from .pdf_utils import render_to_pdf, pdf_http_response

def home(request):
    return render(request, "core/home.html")

@login_required
def viviendas_list(request):
    qs = Vivienda.objects.select_related("proyecto").all()[:100]
    return render(request, "core/viviendas_list.html", {"viviendas": qs})

@login_required
def proyectos_list(request):
    qs = Proyecto.objects.all()[:100]
    return render(request, "core/proyectos_list.html", {"proyectos": qs})

@login_required
def reportes_home(request):
    proyectos = Proyecto.objects.all().order_by("codigo")
    return render(request, "core/reportes_home.html", {"proyectos": proyectos})

@login_required
def reporte_proyecto_pdf(request):
    proyecto_id = request.GET.get("proyecto_id") or request.POST.get("proyecto_id")
    if not proyecto_id:
        return HttpResponseBadRequest("Falta proyecto_id")

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return HttpResponseBadRequest("Proyecto no existe")

    # Obtener registros de postventa (primero el queryset completo, sin slice)
    registros_qs = (RegistroPostventa.objects
                    .filter(proyecto=proyecto)
                    .select_related('proyecto')
                    .order_by("-creado_en"))
    
    # Calcular estadísticas generales (ANTES del slice)
    total_registros = registros_qs.count()
    urgentes = registros_qs.filter(urgencia="ALTA").count()
    
    # Calcular distribución por urgencia (ANTES del slice)
    por_urgencia = []
    if total_registros > 0:
        urgencia_counts = registros_qs.values('urgencia').annotate(total=Count('id'))
        for item in urgencia_counts:
            urgencia = item['urgencia'] or 'BAJA'
            total = item['total']
            porcentaje = (total / total_registros) * 100
            por_urgencia.append({
                'urgencia': urgencia,
                'total': total,
                'porcentaje': porcentaje
            })
    
    # AHORA SÍ aplicar el slice para limitar los registros en el PDF
    registros = list(registros_qs[:200])
    
    # Obtener viviendas con información adicional
    viviendas = (Vivienda.objects
                 .filter(proyecto=proyecto)
                 .prefetch_related('perfilusuario_set')
                 .annotate(num_registros=Count('fichainmueble__registropostventa')))
    
    # Contar evidencias
    evidencias_count = Evidencia.objects.filter(registro__proyecto=proyecto).count()
    
    stats = {
        "viviendas": viviendas.count(),
        "registros": total_registros,
        "urgentes": urgentes,
        "evidencias": evidencias_count,
        "por_urgencia": por_urgencia,
    }

    ctx = {
        "proyecto": proyecto,
        "registros": registros,
        "viviendas": list(viviendas[:50]),  # Limitar a 50 viviendas para el PDF
        "stats": stats,
        "generado_en": timezone.localtime(),
    }

    pdf_bytes = render_to_pdf("reports/proyecto_pdf.html", ctx)
    if not pdf_bytes:
        return HttpResponseBadRequest("No se pudo generar PDF")

    filename = f"reporte_{proyecto.codigo}_{timezone.now().strftime('%Y%m%d')}.pdf"
    return pdf_http_response(filename, pdf_bytes, as_attachment=True)

@login_required
def reporte_proyecto_enviar(request):
    proyecto_id = request.GET.get("proyecto_id") or request.POST.get("proyecto_id")
    to_addr = request.GET.get("to") or request.POST.get("to")
    if not proyecto_id or not to_addr:
        return HttpResponseBadRequest("Falta proyecto_id o correo destino")

    try:
        proyecto = Proyecto.objects.get(id=proyecto_id)
    except Proyecto.DoesNotExist:
        return HttpResponseBadRequest("Proyecto no existe")

    # Obtener registros de postventa (primero el queryset completo, sin slice)
    registros_qs = (RegistroPostventa.objects
                    .filter(proyecto=proyecto)
                    .select_related('proyecto')
                    .order_by("-creado_en"))
    
    # Calcular estadísticas generales (ANTES del slice)
    total_registros = registros_qs.count()
    urgentes = registros_qs.filter(urgencia="ALTA").count()
    
    # Calcular distribución por urgencia (ANTES del slice)
    por_urgencia = []
    if total_registros > 0:
        urgencia_counts = registros_qs.values('urgencia').annotate(total=Count('id'))
        for item in urgencia_counts:
            urgencia = item['urgencia'] or 'BAJA'
            total = item['total']
            porcentaje = (total / total_registros) * 100
            por_urgencia.append({
                'urgencia': urgencia,
                'total': total,
                'porcentaje': porcentaje
            })
    
    # AHORA SÍ aplicar el slice para limitar los registros en el PDF
    registros = list(registros_qs[:200])
    
    # Obtener viviendas con información adicional
    viviendas = (Vivienda.objects
                 .filter(proyecto=proyecto)
                 .prefetch_related('perfilusuario_set')
                 .annotate(num_registros=Count('fichainmueble__registropostventa')))
    
    # Contar evidencias
    evidencias_count = Evidencia.objects.filter(registro__proyecto=proyecto).count()
    
    stats = {
        "viviendas": viviendas.count(),
        "registros": total_registros,
        "urgentes": urgentes,
        "evidencias": evidencias_count,
        "por_urgencia": por_urgencia,
    }

    ctx = {
        "proyecto": proyecto,
        "registros": registros,
        "viviendas": list(viviendas[:50]),  # Limitar a 50 viviendas para el PDF
        "stats": stats,
        "generado_en": timezone.localtime(),
    }

    pdf_bytes = render_to_pdf("reports/proyecto_pdf.html", ctx)
    if not pdf_bytes:
        return HttpResponseBadRequest("No se pudo generar PDF")

    # Preparar email con información detallada
    fecha_generacion = timezone.localtime().strftime("%d de %B de %Y a las %H:%M")
    filename = f"reporte_{proyecto.codigo}_{timezone.now().strftime('%Y%m%d')}.pdf"
    
    body = f"""Estimado/a,

Adjunto encontrará el Informe de Recepción y Postventa del Proyecto:

• Código: {proyecto.codigo}
• Nombre: {proyecto.nombre}
• Ubicación: {proyecto.ubicacion or 'No especificada'}

RESUMEN:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total de Viviendas: {stats['viviendas']}
• Registros de Postventa: {stats['registros']}
• Observaciones Urgentes: {stats['urgentes']}
• Evidencias Adjuntas: {stats['evidencias']}

Este reporte fue generado automáticamente el {fecha_generacion}.

Para cualquier consulta, no dude en contactarnos.

Saludos cordiales,
TECHO Chile
Plataforma de Recepción y Postventa Habitacional

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Este correo y sus adjuntos contienen información confidencial.
"""
    
    # Enviar email
    subject = f"Reporte Proyecto {proyecto.codigo} - {proyecto.nombre}"
    email = EmailMessage(subject=subject, body=body, to=[to_addr])
    email.attach(filename=filename, content=pdf_bytes, mimetype="application/pdf")
    email.send(fail_silently=False)
    
    messages.success(request, f"✓ Reporte enviado exitosamente a {to_addr}")
    return redirect("reportes_home")

# --- Admin: Proyectos (HTMX modales) ---
@login_required
@require_role("Admin")
def admin_proyectos(request):
    qs = Proyecto.objects.all().order_by("codigo")
    # Si es una petición HTMX para solo el tbody, devolver solo eso
    if request.headers.get('HX-Request') and request.headers.get('HX-Target') == 'tb-proy':
        return render(request, "partials/proyectos_table.html", {"proyectos": qs})
    return render(request, "adminx/proyectos.html", {"proyectos": qs})

@login_required
@require_role("Admin")
def admin_proyecto_form(request, pk=None):
    obj = get_object_or_404(Proyecto, pk=pk) if pk else None
    if request.method == "POST":
        form = ProyectoForm(request.POST, instance=obj)
        if form.is_valid():
            proyecto = form.save()
            # Si es una petición HTMX, devolver script para cerrar modal y actualizar tabla
            if request.headers.get('HX-Request'):
                proyectos = Proyecto.objects.all().order_by("codigo")
                return render(request, "partials/proyecto_saved.html", {
                    "proyectos": proyectos,
                    "proyecto": proyecto
                })
            return redirect("admin_proyectos")
        return render(request, "partials/form_proyecto.html", {"form": form}, status=400)
    form = ProyectoForm(instance=obj)
    return render(request, "partials/form_proyecto.html", {"form": form})

@login_required
@require_role("Admin")
@require_POST
def admin_proyecto_delete(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    proyecto.delete()
    # Si es una petición HTMX, devolver un string vacío para eliminar la fila
    if request.headers.get('HX-Request'):
        return HttpResponse("")
    return redirect("admin_proyectos")

# --- Trabajador: subir evidencia a un registro ---
@login_required
@require_role("Trabajador","Admin")
def subir_evidencia(request, reg_id):
    reg = get_object_or_404(RegistroPostventa, pk=reg_id)
    if request.method == "POST":
        form = EvidenciaForm(request.POST, request.FILES)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.registro = reg
            ev.subido_por = request.user
            ev.save()
            # responde con la fila/galería actualizada (HTMX)
            evidencias = reg.evidencias.order_by("-creado_en")
            return render(request, "partials/evidencias_list.html", {"evidencias": evidencias})
        return HttpResponseBadRequest("Formulario inválido")
    else:
        form = EvidenciaForm()
        return render(request, "partials/evidencia_form.html", {"form": form, "reg": reg})

# --- Trabajador: cambiar estado de registro ---
@login_required
@require_role("Trabajador","Admin")
@require_POST
def cambiar_estado_registro(request, reg_id):
    reg = get_object_or_404(RegistroPostventa, pk=reg_id)
    nuevo = request.POST.get("estado")
    if nuevo not in dict(ESTADOS):
        return HttpResponseBadRequest("Estado inválido")
    reg.estado = nuevo
    reg.save()
    return HttpResponse("OK")


# =============================================================================
# SISTEMA DE MONITOREO DS 49 (120 DÍAS POST-ENTREGA)
# =============================================================================

@login_required
@require_role("Admin", "Trabajador")
def monitoreo_ds49(request):
    """
    Vista para monitorear el cumplimiento del DS 49 (120 días post-entrega)
    Muestra todas las fichas con fecha de entrega y su estado
    """
    from .models import FichaInmueble
    
    # Obtener todas las fichas con fecha de entrega
    fichas = (FichaInmueble.objects
              .select_related('proyecto', 'vivienda')
              .filter(fecha_entrega__isnull=False)
              .order_by('fecha_entrega'))
    
    # Clasificar por estado
    fichas_data = []
    contadores = {
        'NORMAL': 0,
        'ADVERTENCIA': 0,
        'CRITICO': 0,
        'VENCIDO': 0,
        'SIN_FECHA': 0,
    }
    
    for ficha in fichas:
        estado = ficha.estado_ds49()
        dias_restantes = ficha.dias_restantes_ds49()
        porcentaje = ficha.porcentaje_ds49()
        
        fichas_data.append({
            'ficha': ficha,
            'estado': estado,
            'dias_restantes': dias_restantes,
            'dias_transcurridos': ficha.dias_desde_entrega(),
            'porcentaje': porcentaje,
        })
        
        contadores[estado] += 1
    
    # Fichas sin fecha de entrega
    fichas_sin_fecha = FichaInmueble.objects.filter(fecha_entrega__isnull=True).count()
    contadores['SIN_FECHA'] = fichas_sin_fecha
    
    context = {
        'rol': request.user.perfil.rol,
        'fichas_data': fichas_data,
        'contadores': contadores,
        'total_fichas': fichas.count() + fichas_sin_fecha,
    }
    
    return render(request, "core/monitoreo_ds49.html", context)


@login_required
@require_role("Admin")
def actualizar_fecha_entrega(request, ficha_id):
    """
    Vista para que el Admin actualice la fecha de entrega de una ficha
    """
    from .models import FichaInmueble
    
    ficha = get_object_or_404(FichaInmueble, pk=ficha_id)
    
    if request.method == "POST":
        fecha_str = request.POST.get("fecha_entrega")
        if fecha_str:
            from datetime import datetime
            try:
                fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
                ficha.fecha_entrega = fecha
                ficha.save()
                messages.success(request, 
                    f"✅ Fecha de entrega actualizada para {ficha.proyecto.codigo} - {ficha.vivienda}")
            except ValueError:
                messages.error(request, "❌ Formato de fecha inválido")
        else:
            messages.error(request, "❌ Debes ingresar una fecha")
        
        return redirect("monitoreo_ds49")
    
    return render(request, "core/actualizar_fecha_entrega.html", {
        "rol": request.user.perfil.rol,
        "ficha": ficha
    })


# =============================================================================
# GESTIÓN DE VIVIENDAS (CRUD COMPLETO PARA ADMIN)
# =============================================================================

@login_required
@require_role("Admin")
def admin_viviendas(request):
    """
    Vista para listar todas las viviendas (con filtros)
    """
    viviendas = Vivienda.objects.select_related('proyecto').all().order_by('proyecto__codigo', 'id')
    proyectos = Proyecto.objects.all().order_by('codigo')
    
    # Filtro por proyecto
    proyecto_id = request.GET.get('proyecto')
    if proyecto_id:
        viviendas = viviendas.filter(proyecto_id=proyecto_id)
    
    # Filtro por tipo
    tipo = request.GET.get('tipo')
    if tipo:
        viviendas = viviendas.filter(tipo=tipo)
    
    context = {
        'rol': request.user.perfil.rol,
        'viviendas': viviendas,
        'proyectos': proyectos,
        'proyecto_filtro': proyecto_id,
        'tipo_filtro': tipo,
    }
    
    return render(request, "core/admin_viviendas.html", context)


@login_required
@require_role("Admin")
def crear_vivienda(request):
    """
    Vista para crear una nueva vivienda
    """
    if request.method == "POST":
        form = ViviendaForm(request.POST)
        if form.is_valid():
            vivienda = form.save()
            
            # Crear automáticamente la ficha de inmueble
            from .models import FichaInmueble
            FichaInmueble.objects.get_or_create(
                proyecto=vivienda.proyecto,
                vivienda=vivienda
            )
            
            messages.success(request, 
                f"✅ Vivienda creada exitosamente en el proyecto {vivienda.proyecto.codigo}")
            return redirect("admin_viviendas")
    else:
        form = ViviendaForm()
    
    proyectos = Proyecto.objects.all().order_by('codigo')
    
    return render(request, "core/crear_vivienda.html", {
        "rol": request.user.perfil.rol,
        "form": form,
        "proyectos": proyectos
    })


@login_required
@require_role("Admin")
def editar_vivienda(request, vivienda_id):
    """
    Vista para editar una vivienda existente
    """
    vivienda = get_object_or_404(Vivienda, pk=vivienda_id)
    
    if request.method == "POST":
        form = ViviendaForm(request.POST, instance=vivienda)
        if form.is_valid():
            vivienda = form.save()
            
            # Actualizar la ficha de inmueble si cambió el proyecto
            from .models import FichaInmueble
            ficha, created = FichaInmueble.objects.get_or_create(
                proyecto=vivienda.proyecto,
                vivienda=vivienda
            )
            
            messages.success(request, 
                f"✅ Vivienda actualizada exitosamente")
            return redirect("admin_viviendas")
    else:
        form = ViviendaForm(instance=vivienda)
    
    proyectos = Proyecto.objects.all().order_by('codigo')
    
    return render(request, "core/editar_vivienda.html", {
        "rol": request.user.perfil.rol,
        "form": form,
        "vivienda": vivienda,
        "proyectos": proyectos
    })


@login_required
@require_role("Admin")
def eliminar_vivienda(request, vivienda_id):
    """
    Vista para eliminar una vivienda con confirmación de seguridad
    """
    vivienda = get_object_or_404(Vivienda, pk=vivienda_id)
    
    if request.method == "POST":
        # Verificar texto de confirmación
        confirmacion = request.POST.get('confirmacion', '').strip()
        texto_esperado = f"acepto eliminar vivienda"
        
        if confirmacion.lower() != texto_esperado:
            messages.error(request, 
                f"⚠️ Debes escribir exactamente: '{texto_esperado}' para confirmar la eliminación")
            return redirect("admin_viviendas")
        
        # Verificar si tiene registros de postventa asociados
        registros_count = RegistroPostventa.objects.filter(
            ficha__vivienda=vivienda
        ).count()
        
        if registros_count > 0:
            messages.error(request, 
                f"❌ No se puede eliminar la vivienda porque tiene {registros_count} registros de postventa asociados")
            return redirect("admin_viviendas")
        
        # Verificar si tiene familias asignadas
        from .models import PerfilUsuario
        familias_count = PerfilUsuario.objects.filter(vivienda_asignada=vivienda).count()
        
        if familias_count > 0:
            messages.error(request, 
                f"❌ No se puede eliminar la vivienda porque tiene {familias_count} familia(s) asignada(s)")
            return redirect("admin_viviendas")
        
        proyecto_codigo = vivienda.proyecto.codigo
        vivienda.delete()
        
        messages.success(request, 
            f"✅ Vivienda eliminada exitosamente del proyecto {proyecto_codigo}")
        return redirect("admin_viviendas")
    
    # Obtener información para mostrar en la confirmación
    from .models import PerfilUsuario
    registros_count = RegistroPostventa.objects.filter(ficha__vivienda=vivienda).count()
    familias_count = PerfilUsuario.objects.filter(vivienda_asignada=vivienda).count()
    
    return render(request, "core/eliminar_vivienda.html", {
        "rol": request.user.perfil.rol,
        "vivienda": vivienda,
        "registros_count": registros_count,
        "familias_count": familias_count,
    })


# =============================================================================
# GESTIÓN DE CONSTRUCTORAS (CRUD COMPLETO PARA ADMIN)
# =============================================================================

@login_required
@require_role("Admin")
def admin_constructoras(request):
    """Vista para listar todas las constructoras"""
    from .models import Constructora
    
    constructoras = Constructora.objects.all().order_by('nombre')
    
    context = {
        'rol': request.user.perfil.rol,
        'constructoras': constructoras,
    }
    
    return render(request, "core/admin_constructoras.html", context)


@login_required
@require_role("Admin")
def crear_constructora(request):
    """Vista para crear una nueva constructora"""
    from .forms import ConstructoraForm
    
    if request.method == "POST":
        form = ConstructoraForm(request.POST)
        if form.is_valid():
            constructora = form.save()
            messages.success(request, 
                f"✅ Constructora '{constructora.nombre}' creada exitosamente")
            return redirect("admin_constructoras")
    else:
        form = ConstructoraForm()
    
    return render(request, "core/crear_constructora.html", {
        "rol": request.user.perfil.rol,
        "form": form
    })


@login_required
@require_role("Admin")
def editar_constructora(request, constructora_id):
    """Vista para editar una constructora existente"""
    from .models import Constructora
    from .forms import ConstructoraForm
    
    constructora = get_object_or_404(Constructora, pk=constructora_id)
    
    if request.method == "POST":
        form = ConstructoraForm(request.POST, instance=constructora)
        if form.is_valid():
            constructora = form.save()
            messages.success(request, 
                f"✅ Constructora '{constructora.nombre}' actualizada exitosamente")
            return redirect("admin_constructoras")
    else:
        form = ConstructoraForm(instance=constructora)
    
    return render(request, "core/editar_constructora.html", {
        "rol": request.user.perfil.rol,
        "form": form,
        "constructora": constructora
    })


@login_required
@require_role("Admin")
def eliminar_constructora(request, constructora_id):
    """Vista para eliminar una constructora con confirmación de seguridad"""
    from .models import Constructora
    
    constructora = get_object_or_404(Constructora, pk=constructora_id)
    
    if request.method == "POST":
        # Verificar texto de confirmación
        confirmacion = request.POST.get('confirmacion', '').strip()
        texto_esperado = f"acepto eliminar constructora"
        
        if confirmacion.lower() != texto_esperado:
            messages.error(request, 
                f"⚠️ Debes escribir exactamente: '{texto_esperado}' para confirmar la eliminación")
            return redirect("admin_constructoras")
        
        # Verificar si tiene proyectos asociados
        proyectos_count = Proyecto.objects.filter(constructora=constructora).count()
        
        if proyectos_count > 0:
            messages.error(request, 
                f"❌ No se puede eliminar la constructora porque tiene {proyectos_count} proyecto(s) asociado(s)")
            return redirect("admin_constructoras")
        
        nombre = constructora.nombre
        constructora.delete()
        
        messages.success(request, 
            f"✅ Constructora '{nombre}' eliminada exitosamente")
        return redirect("admin_constructoras")
    
    # Obtener información para mostrar en la confirmación
    proyectos_count = Proyecto.objects.filter(constructora=constructora).count()
    
    return render(request, "core/eliminar_constructora.html", {
        "rol": request.user.perfil.rol,
        "constructora": constructora,
        "proyectos_count": proyectos_count,
    })


# =============================================================================
# FORMULARIO DE OBSERVACIONES PARA FAMILIAS
# =============================================================================

@login_required
def reportar_observacion_familia(request):
    """Vista para que las familias reporten observaciones de su vivienda"""
    from .forms import ObservacionFamiliaForm
    from django.contrib import messages
    
    perfil = request.user.perfil
    
    # Solo las familias pueden acceder
    if perfil.rol != "Familia":
        messages.error(request, "Esta función es solo para familias")
        return redirect("dashboard")
    
    # Verificar que la familia tenga vivienda asignada
    if not perfil.vivienda_asignada:
        messages.error(request, "Tu vivienda aún no ha sido vinculada. Contacta con el administrador.")
        return redirect("dashboard")
    
    vivienda = perfil.vivienda_asignada
    
    if request.method == "POST":
        form = ObservacionFamiliaForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Obtener la ficha de inmueble
            try:
                ficha = FichaInmueble.objects.get(
                    proyecto=vivienda.proyecto,
                    vivienda=vivienda
                )
            except FichaInmueble.DoesNotExist:
                # Crear la ficha si no existe
                ficha = FichaInmueble.objects.create(
                    proyecto=vivienda.proyecto,
                    vivienda=vivienda
                )
            
            # Crear el registro de observación
            registro = form.save(commit=False)
            registro.proyecto = vivienda.proyecto
            registro.ficha = ficha
            registro.reportante = request.user
            registro.save()
            
            # Procesar evidencias (archivos múltiples)
            archivos = request.FILES.getlist('evidencias')
            evidencias_creadas = 0
            
            for archivo in archivos[:5]:  # Máximo 5 archivos
                if archivo.size <= 10 * 1024 * 1024:  # Máximo 10 MB por archivo
                    Evidencia.objects.create(
                        registro=registro,
                        archivo=archivo,
                        comentario=f"Evidencia subida por {request.user.username}",
                        subido_por=request.user
                    )
                    evidencias_creadas += 1
            
            # Mensaje de éxito
            mensaje = f"✅ Tu observación sobre '{registro.recinto}' ha sido registrada exitosamente."
            if evidencias_creadas > 0:
                mensaje += f" Se guardaron {evidencias_creadas} archivo(s) de evidencia."
            
            messages.success(request, mensaje)
            return redirect("dashboard")
    else:
        form = ObservacionFamiliaForm()
    
    context = {
        'rol': perfil.rol,
        'form': form,
        'vivienda': vivienda,
    }
    
    return render(request, "core/reportar_observacion_familia.html", context)


# =============================================================================
# ASIGNACIÓN DE VIVIENDAS POR RUT
# =============================================================================

@login_required
@require_role("Admin")
def buscar_familia_por_rut(request):
    """Vista para buscar familias por RUT y asignar viviendas"""
    from .utils import validar_rut
    
    perfil = request.user.perfil
    familias = []
    rut_busqueda = None
    viviendas_disponibles = Vivienda.objects.select_related('proyecto').filter(
        perfilusuario__isnull=True  # Viviendas sin familia asignada
    ).order_by('proyecto__codigo')
    
    if request.method == "POST":
        accion = request.POST.get('accion')
        
        if accion == 'buscar':
            rut_busqueda = request.POST.get('rut', '').strip()
            
            if rut_busqueda:
                # Validar RUT
                es_valido, rut_formateado = validar_rut(rut_busqueda)
                
                if es_valido:
                    # Buscar por RUT exacto (limpio)
                    from .utils import limpiar_rut
                    rut_limpio = limpiar_rut(rut_busqueda)
                    
                    familias = PerfilUsuario.objects.filter(
                        rol="Familia",
                        rut__icontains=rut_limpio[:8]  # Buscar por los primeros 8 dígitos
                    ).select_related('user', 'vivienda_asignada', 'vivienda_asignada__proyecto')
                    
                    if not familias.exists():
                        messages.warning(request, 
                            f"No se encontraron familias con RUT {rut_formateado}")
                    else:
                        messages.success(request, 
                            f"Se encontraron {familias.count()} familia(s) con RUT similar a {rut_formateado}")
                else:
                    messages.error(request, "El RUT ingresado no es válido")
        
        elif accion == 'asignar':
            perfil_id = request.POST.get('perfil_id')
            vivienda_id = request.POST.get('vivienda_id')
            
            try:
                perfil_familia = PerfilUsuario.objects.get(id=perfil_id, rol="Familia")
                vivienda = Vivienda.objects.get(id=vivienda_id)
                
                # Verificar que la vivienda no esté asignada
                if PerfilUsuario.objects.filter(vivienda_asignada=vivienda).exclude(id=perfil_id).exists():
                    messages.error(request, 
                        f"La vivienda ya está asignada a otra familia")
                else:
                    # Asignar vivienda
                    perfil_familia.vivienda_asignada = vivienda
                    perfil_familia.save()
                    
                    messages.success(request, 
                        f"✅ Vivienda {vivienda.proyecto.codigo}-{vivienda.id} asignada exitosamente a {perfil_familia.get_nombre_completo()}")
                    
                    return redirect('buscar_familia_por_rut')
            
            except PerfilUsuario.DoesNotExist:
                messages.error(request, "Familia no encontrada")
            except Vivienda.DoesNotExist:
                messages.error(request, "Vivienda no encontrada")
        
        elif accion == 'desasignar':
            perfil_id = request.POST.get('perfil_id')
            
            try:
                perfil_familia = PerfilUsuario.objects.get(id=perfil_id, rol="Familia")
                vivienda_anterior = perfil_familia.vivienda_asignada
                
                perfil_familia.vivienda_asignada = None
                perfil_familia.save()
                
                messages.success(request, 
                    f"✅ Vivienda {vivienda_anterior.proyecto.codigo}-{vivienda_anterior.id} desasignada de {perfil_familia.get_nombre_completo()}")
                
                return redirect('buscar_familia_por_rut')
            
            except PerfilUsuario.DoesNotExist:
                messages.error(request, "Familia no encontrada")
    
    context = {
        'rol': perfil.rol,
        'familias': familias,
        'rut_busqueda': rut_busqueda,
        'viviendas_disponibles': viviendas_disponibles,
        'total_viviendas_disponibles': viviendas_disponibles.count(),
    }
    
    return render(request, "core/buscar_familia_rut.html", context)


# ============================================
# NUEVAS VISTAS - FICHA DE INMUEBLES
# ============================================

@login_required
@require_role("Admin", "Trabajador")
def fichas_inmuebles(request):
    """Vista para ver todas las fichas de inmuebles con observaciones"""
    perfil = request.user.perfil
    
    # Obtener parámetros de búsqueda
    proyecto_id = request.GET.get('proyecto')
    busqueda = request.GET.get('q', '').strip()
    
    # Filtrar fichas según rol
    if perfil.rol == "Admin":
        fichas = FichaInmueble.objects.select_related(
            'proyecto', 'vivienda'
        ).prefetch_related('registropostventa_set')
    else:  # Trabajador
        if perfil.proyecto_asignado:
            fichas = FichaInmueble.objects.filter(
                proyecto=perfil.proyecto_asignado
            ).select_related('proyecto', 'vivienda').prefetch_related('registropostventa_set')
        else:
            fichas = FichaInmueble.objects.none()
    
    # Aplicar filtros
    if proyecto_id:
        fichas = fichas.filter(proyecto_id=proyecto_id)
    
    if busqueda:
        fichas = fichas.filter(
            Q(vivienda__rut_propietario__icontains=busqueda) |
            Q(vivienda__direccion__icontains=busqueda) |
            Q(vivienda__numero__icontains=busqueda) |
            Q(proyecto__codigo__icontains=busqueda) |
            Q(proyecto__nombre__icontains=busqueda)
        )
    
    # Anotar cantidad de observaciones
    fichas = fichas.annotate(
        total_observaciones=Count('registropostventa'),
        observaciones_pendientes=Count('registropostventa', filter=Q(registropostventa__estado='PENDIENTE')),
        observaciones_urgentes=Count('registropostventa', filter=Q(registropostventa__urgencia='ALTA'))
    ).order_by('-observaciones_urgentes', '-total_observaciones')
    
    # Obtener proyectos para el filtro
    if perfil.rol == "Admin":
        proyectos = Proyecto.objects.all().order_by('codigo')
    else:
        proyectos = Proyecto.objects.filter(id=perfil.proyecto_asignado_id) if perfil.proyecto_asignado else []
    
    context = {
        'rol': perfil.rol,
        'fichas': fichas[:100],  # Limitar a 100 para rendimiento
        'proyectos': proyectos,
        'proyecto_seleccionado': proyecto_id,
        'busqueda': busqueda,
    }
    
    return render(request, 'core/fichas_inmuebles.html', context)


@login_required
@require_role("Admin", "Trabajador")
def detalle_ficha_inmueble(request, ficha_id):
    """Vista detallada de una ficha de inmueble con todas sus observaciones"""
    perfil = request.user.perfil
    
    ficha = get_object_or_404(
        FichaInmueble.objects.select_related('proyecto', 'vivienda'),
        id=ficha_id
    )
    
    # Verificar permisos
    if perfil.rol == "Trabajador" and ficha.proyecto != perfil.proyecto_asignado:
        messages.error(request, "No tienes permisos para ver esta ficha")
        return redirect('fichas_inmuebles')
    
    # Obtener observaciones con evidencias
    observaciones = RegistroPostventa.objects.filter(
        ficha=ficha
    ).select_related('reportante').prefetch_related('evidencia_set').order_by('-creado_en')
    
    # Añadir evidencias a cada observación
    for obs in observaciones:
        obs.evidencias = obs.evidencia_set.all()
    
    # Obtener perfil del propietario si existe
    propietario = None
    if ficha.vivienda.rut_propietario:
        try:
            propietario = PerfilUsuario.objects.filter(
                rut=ficha.vivienda.rut_propietario
            ).select_related('user').first()
        except:
            pass
    
    # Calcular días en postventa
    dias_postventa = 0
    if ficha.proyecto.fecha_entrega:
        dias_postventa = (timezone.now().date() - ficha.proyecto.fecha_entrega).days
    
    context = {
        'rol': perfil.rol,
        'ficha': ficha,
        'vivienda': ficha.vivienda,
        'proyecto': ficha.proyecto,
        'observaciones': observaciones,
        'propietario': propietario,
        'total_observaciones': observaciones.count(),
        'observaciones_pendientes': observaciones.filter(estado='PENDIENTE').count(),
        'observaciones_urgentes': observaciones.filter(urgencia='ALTA').count(),
        'dias_postventa': dias_postventa,
    }
    
    return render(request, 'core/detalle_ficha_inmueble.html', context)


@login_required
@require_role("Admin")
def buscar_usuario_por_rut(request):
    """API para buscar usuario por RUT (para autocompletar en formulario de vivienda)"""
    rut = request.GET.get('rut', '').strip()
    
    if not rut:
        return JsonResponse({'error': 'RUT requerido'}, status=400)
    
    try:
        perfil = PerfilUsuario.objects.filter(rut=rut).select_related('user').first()
        
        if perfil:
            return JsonResponse({
                'found': True,
                'nombre': perfil.nombre,
                'apellido': perfil.apellido,
                'nombre_completo': perfil.get_nombre_completo(),
                'telefono': perfil.telefono or '',
                'direccion': perfil.direccion or '',
                'ciudad': perfil.ciudad or '',
                'comuna': perfil.comuna or '',
                'region': perfil.region or '',
                'correo': perfil.user.email if perfil.user else '',
                'rol': perfil.rol,
            })
        else:
            return JsonResponse({'found': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)