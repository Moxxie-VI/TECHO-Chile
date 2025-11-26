from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import require_role
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import EmailMessage
from django.db.models import Count, Q
from .forms import ProyectoForm, ViviendaForm, RegistroPostventaForm, EvidenciaForm, RegistroComentarioForm
from .models import Proyecto, Vivienda, RegistroPostventa, Evidencia, ESTADOS, FichaInmueble, PerfilUsuario, RegistroComentario, Notificacion
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
def ver_informe_general(request):
    """
    Vista HTML del informe general - permite visualizar antes de descargar PDF
    """
    from .models import Constructora
    
    # KPIs Principales
    total_proyectos = Proyecto.objects.count()
    total_viviendas = Vivienda.objects.count()
    total_observaciones = RegistroPostventa.objects.count()
    
    # Estado de proyectos y viviendas
    proyectos_finalizados = Proyecto.objects.filter(estado='FINALIZADO').count()
    proyectos_activos = total_proyectos - proyectos_finalizados
    
    total_constructoras = Constructora.objects.count()
    
    # Viviendas - Modelo no tiene campo 'estado'
    viviendas_entregadas = 0
    viviendas_pendientes = 0
    porcentaje_entrega = 0
    
    # Observaciones de postventa
    obs_resueltas = RegistroPostventa.objects.filter(estado='RESUELTO').count()
    obs_pendientes = RegistroPostventa.objects.filter(estado='PENDIENTE').count()
    obs_alta_urgencia = RegistroPostventa.objects.filter(urgencia='ALTA', estado='PENDIENTE').count()
    
    tasa_resolucion = (obs_resueltas / total_observaciones * 100) if total_observaciones > 0 else 0
    porcentaje_resueltas = (obs_resueltas / total_observaciones * 100) if total_observaciones > 0 else 0
    porcentaje_pendientes = (obs_pendientes / total_observaciones * 100) if total_observaciones > 0 else 0
    porcentaje_alta_urgencia = (obs_alta_urgencia / total_observaciones * 100) if total_observaciones > 0 else 0
    
    # Distribución geográfica
    distribucion_regiones = (
        Proyecto.objects
        .values('region')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    top_comunas = (
        Proyecto.objects
        .values('comuna')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Top Constructoras
    constructoras = Constructora.objects.all()
    top_constructoras_data = []
    
    for constructora in constructoras:
        proyectos_constructora = Proyecto.objects.filter(constructora=constructora)
        num_proyectos = proyectos_constructora.count()
        
        if num_proyectos > 0:
            obs_total = RegistroPostventa.objects.filter(proyecto__constructora=constructora).count()
            obs_resueltas_c = RegistroPostventa.objects.filter(proyecto__constructora=constructora, estado='RESUELTO').count()
            
            tasa_resolucion_c = (obs_resueltas_c / obs_total * 100) if obs_total > 0 else 0
            score = tasa_resolucion_c
            
            top_constructoras_data.append({
                'nombre': constructora.nombre,
                'num_proyectos': num_proyectos,
                'score': score,
                'tasa_resolucion': tasa_resolucion_c
            })
    
    top_constructoras = sorted(top_constructoras_data, key=lambda x: x['score'], reverse=True)[:10]
    
    # Proyectos recientes (ordenados por fecha de inicio)
    proyectos_recientes = Proyecto.objects.order_by('-fecha_inicio')[:10]
    
    # Distribución de fallas por recinto
    distribucion_recintos = (
        RegistroPostventa.objects
        .values('recinto')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')[:10]
    )
    
    distribucion_recintos_list = []
    for item in distribucion_recintos:
        porcentaje = (item['cantidad'] / total_observaciones * 100) if total_observaciones > 0 else 0
        distribucion_recintos_list.append({
            'recinto': item['recinto'] or 'No especificado',
            'cantidad': item['cantidad'],
            'porcentaje': porcentaje
        })
    
    ctx = {
        'fecha_generacion': timezone.localtime(),
        'total_proyectos': total_proyectos,
        'total_viviendas': total_viviendas,
        'total_observaciones': total_observaciones,
        'tasa_resolucion': tasa_resolucion,
        'proyectos_activos': proyectos_activos,
        'proyectos_finalizados': proyectos_finalizados,
        'total_constructoras': total_constructoras,
        'viviendas_entregadas': viviendas_entregadas,
        'viviendas_pendientes': viviendas_pendientes,
        'porcentaje_entrega': porcentaje_entrega,
        'obs_resueltas': obs_resueltas,
        'obs_pendientes': obs_pendientes,
        'obs_alta_urgencia': obs_alta_urgencia,
        'porcentaje_resueltas': porcentaje_resueltas,
        'porcentaje_pendientes': porcentaje_pendientes,
        'porcentaje_alta_urgencia': porcentaje_alta_urgencia,
        'distribucion_regiones': distribucion_regiones,
        'top_comunas': top_comunas,
        'top_constructoras': top_constructoras,
        'proyectos_recientes': proyectos_recientes,
        'distribucion_recintos': distribucion_recintos_list,
    }
    
    return render(request, 'core/informe_general.html', ctx)

@login_required
def reporte_general_pdf(request):
    """
    Genera un informe general consolidado de todos los proyectos
    con KPIs, distribución geográfica, rankings y métricas clave
    """
    from .models import Constructora
    import os
    from django.conf import settings
    
    # KPIs Principales
    total_proyectos = Proyecto.objects.count()
    total_viviendas = Vivienda.objects.count()
    total_observaciones = RegistroPostventa.objects.count()
    
    # Estado de proyectos y viviendas
    # Asumimos que proyectos sin estado 'FINALIZADO' están activos
    proyectos_finalizados = Proyecto.objects.filter(estado='FINALIZADO').count()
    proyectos_activos = total_proyectos - proyectos_finalizados
    
    total_constructoras = Constructora.objects.count()
    
    # Viviendas - Modelo no tiene campo 'estado'
    viviendas_entregadas = 0
    viviendas_pendientes = 0
    porcentaje_entrega = 0
    
    # Observaciones de postventa
    obs_resueltas = RegistroPostventa.objects.filter(estado='RESUELTO').count()
    obs_pendientes = RegistroPostventa.objects.filter(estado='PENDIENTE').count()
    obs_alta_urgencia = RegistroPostventa.objects.filter(urgencia='ALTA', estado='PENDIENTE').count()
    
    tasa_resolucion = (obs_resueltas / total_observaciones * 100) if total_observaciones > 0 else 0
    porcentaje_resueltas = (obs_resueltas / total_observaciones * 100) if total_observaciones > 0 else 0
    porcentaje_pendientes = (obs_pendientes / total_observaciones * 100) if total_observaciones > 0 else 0
    porcentaje_alta_urgencia = (obs_alta_urgencia / total_observaciones * 100) if total_observaciones > 0 else 0
    
    # Distribución geográfica - Por Región
    distribucion_regiones = (
        Proyecto.objects
        .values('region')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Distribución geográfica - Top Comunas
    top_comunas = (
        Proyecto.objects
        .values('comuna')
        .annotate(count=Count('id'))
        .order_by('-count')[:10]
    )
    
    # Top Constructoras con score calculado
    constructoras = Constructora.objects.all()
    top_constructoras_data = []
    
    for constructora in constructoras:
        proyectos_constructora = Proyecto.objects.filter(constructora=constructora)
        num_proyectos = proyectos_constructora.count()
        
        if num_proyectos > 0:
            # Calcular observaciones para esta constructora
            obs_total = RegistroPostventa.objects.filter(proyecto__constructora=constructora).count()
            obs_resueltas_c = RegistroPostventa.objects.filter(proyecto__constructora=constructora, estado='RESUELTO').count()
            
            tasa_resolucion_c = (obs_resueltas_c / obs_total * 100) if obs_total > 0 else 0
            
            # Calcular score simplificado (basado en tasa de resolución)
            score = tasa_resolucion_c
            
            top_constructoras_data.append({
                'nombre': constructora.nombre,
                'num_proyectos': num_proyectos,
                'score': score,
                'tasa_resolucion': tasa_resolucion_c
            })
    
    # Ordenar por score descendente y tomar top 10
    top_constructoras = sorted(top_constructoras_data, key=lambda x: x['score'], reverse=True)[:10]
    
    # Proyectos recientes (ordenados por fecha de inicio)
    proyectos_recientes = Proyecto.objects.order_by('-fecha_inicio')[:10]
    
    # Distribución de fallas por recinto
    distribucion_recintos = (
        RegistroPostventa.objects
        .values('recinto')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')[:10]
    )
    
    # Calcular porcentajes para distribución de recintos
    distribucion_recintos_list = []
    for item in distribucion_recintos:
        porcentaje = (item['cantidad'] / total_observaciones * 100) if total_observaciones > 0 else 0
        distribucion_recintos_list.append({
            'recinto': item['recinto'] or 'No especificado',
            'cantidad': item['cantidad'],
            'porcentaje': porcentaje
        })
    
    # Ruta del logo
    logo_path = os.path.join(settings.STATIC_ROOT or settings.BASE_DIR / 'static', 'img', 'techo_logo.png')
    
    # Contexto para el template
    ctx = {
        'fecha_generacion': timezone.localtime(),
        'logo_path': logo_path,
        
        # KPIs principales
        'total_proyectos': total_proyectos,
        'total_viviendas': total_viviendas,
        'total_observaciones': total_observaciones,
        'tasa_resolucion': tasa_resolucion,
        
        # Estado general
        'proyectos_activos': proyectos_activos,
        'proyectos_finalizados': proyectos_finalizados,
        'total_constructoras': total_constructoras,
        
        # Viviendas
        'viviendas_entregadas': viviendas_entregadas,
        'viviendas_pendientes': viviendas_pendientes,
        'porcentaje_entrega': porcentaje_entrega,
        
        # Postventa
        'obs_resueltas': obs_resueltas,
        'obs_pendientes': obs_pendientes,
        'obs_alta_urgencia': obs_alta_urgencia,
        'porcentaje_resueltas': porcentaje_resueltas,
        'porcentaje_pendientes': porcentaje_pendientes,
        'porcentaje_alta_urgencia': porcentaje_alta_urgencia,
        
        # Distribución
        'distribucion_regiones': distribucion_regiones,
        'top_comunas': top_comunas,
        'top_constructoras': top_constructoras,
        'proyectos_recientes': proyectos_recientes,
        'distribucion_recintos': distribucion_recintos_list,
    }
    
    pdf_bytes = render_to_pdf("reports/informe_general.html", ctx)
    if not pdf_bytes:
        return HttpResponseBadRequest("No se pudo generar el PDF")
    
    filename = f"informe_general_techo_{timezone.now().strftime('%Y%m%d_%H%M')}.pdf"
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
    
    estado_anterior = reg.estado
    reg.estado = nuevo
    reg.save()
    
    # 🔔 NOTIFICACIÓN AUTOMÁTICA cuando se resuelve una observación
    if nuevo == "RESUELTO" and estado_anterior != "RESUELTO":
        # Notificar a la familia propietaria de la vivienda
        if reg.vivienda and hasattr(reg.vivienda, 'perfilusuario_set'):
            for perfil in reg.vivienda.perfilusuario_set.filter(rol='Familia'):
                crear_notificacion(
                    usuario=perfil.user,
                    tipo='OBSERVACION_RESUELTA',
                    titulo='¡Tu observación ha sido resuelta!',
                    mensaje=f'La observación en {reg.recinto} ha sido marcada como resuelta.',
                    url_destino=f'/dashboard/'
                )

    next_url = request.POST.get("next")
    if next_url:
        messages.success(request, "Estado actualizado correctamente.")
        return redirect(next_url)

    if request.headers.get("HX-Request"):
        return HttpResponse("OK")

    messages.success(request, "Estado actualizado correctamente.")
    return redirect("dashboard")


@login_required
@require_role("Admin", "Trabajador")
@require_POST
def agregar_comentario_registro(request, reg_id):
    registro = get_object_or_404(
        RegistroPostventa.objects.select_related("proyecto"),
        id=reg_id
    )

    perfil = getattr(request.user, "perfil", None)
    if perfil and perfil.rol == "Trabajador":
        proyecto_asignado = getattr(perfil, "proyecto_asignado", None)
        if not proyecto_asignado or proyecto_asignado.id != registro.proyecto_id:
            messages.error(request, "Este registro no pertenece a tu proyecto asignado.")
            return redirect("detalle_registro_postventa", registro_id=reg_id)

    form = RegistroComentarioForm(request.POST)
    if form.is_valid():
        comentario = form.save(commit=False)
        comentario.registro = registro
        comentario.autor = request.user
        comentario.save()
        
        # 🔔 NOTIFICACIÓN AUTOMÁTICA - Nuevo comentario agregado
        # Notificar a la familia propietaria
        if registro.ficha and registro.ficha.vivienda and hasattr(registro.ficha.vivienda, 'perfilusuario_set'):
            for perfil in registro.ficha.vivienda.perfilusuario_set.filter(rol='Familia'):
                # No notificar si el autor es la misma familia
                if perfil.user != request.user:
                    crear_notificacion(
                        usuario=perfil.user,
                        tipo='COMENTARIO_AGREGADO',
                        titulo='Nuevo comentario en tu observación',
                        mensaje=f'{request.user.username}: {comentario.texto[:100]}...',
                        url_destino=f'/fichas-inmuebles/'
                    )
        
        messages.success(request, "Comentario agregado correctamente.")
    else:
        messages.error(request, "No pudimos guardar tu comentario. Revisa el formulario.")

    return redirect("detalle_registro_postventa", registro_id=reg_id)


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
    """Vista para listar todas las constructoras con KPIs y ranking dinámico"""
    from .models import Constructora
    from django.db.models import Count, Q
    
    constructoras = Constructora.objects.all().order_by('nombre')
    
    # Calcular KPIs y Score para cada constructora
    constructoras_data = []
    for constructora in constructoras:
        # Obtener proyectos y observaciones de esta constructora
        proyectos = Proyecto.objects.filter(constructora=constructora)
        observaciones = RegistroPostventa.objects.filter(proyecto__in=proyectos)
        
        total_obs = observaciones.count()
        obs_resueltas = observaciones.filter(estado='RESUELTA').count()
        obs_pendientes = observaciones.filter(estado__in=['ABIERTA', 'EN_GESTION']).count()
        obs_alta_pendientes = observaciones.filter(
            urgencia='ALTA', 
            estado__in=['ABIERTA', 'EN_GESTION']
        ).count()
        
        # SCORE COMPONENT 1: Tasa de Resolución (40 puntos)
        tasa_resolucion = (obs_resueltas / total_obs * 100) if total_obs > 0 else 100
        score_resolucion = (tasa_resolucion / 100) * 40
        
        # SCORE COMPONENT 2: Calidad - Penalización por urgencias altas sin resolver (30 puntos)
        if total_obs > 0:
            ratio_alta_pendiente = obs_alta_pendientes / total_obs
            score_calidad = 30 - (ratio_alta_pendiente * 30)
        else:
            score_calidad = 30  # Sin observaciones = perfecto
        
        # SCORE COMPONENT 3: Eficiencia - Menos problemas = mejor (30 puntos)
        if total_obs == 0:
            score_eficiencia = 30
        elif total_obs <= 5:
            score_eficiencia = 30
        elif total_obs >= 50:
            score_eficiencia = 0
        else:
            score_eficiencia = 30 - ((total_obs - 5) / 45 * 30)
        
        # SCORE TOTAL
        score_total = score_resolucion + score_calidad + score_eficiencia
        
        # RANKING
        if score_total >= 80:
            ranking = 'ORO'
            ranking_icon = '🥇'
            ranking_color = '#fbbf24'
            ranking_badge = 'warning'  # Bootstrap color
        elif score_total >= 60:
            ranking = 'PLATA'
            ranking_icon = '🥈'
            ranking_color = '#9ca3af'
            ranking_badge = 'secondary'
        elif score_total >= 40:
            ranking = 'BRONCE'
            ranking_icon = '🥉'
            ranking_color = '#cd7f32'
            ranking_badge = 'primary'
        else:
            ranking = 'CRITICO'
            ranking_icon = '⚠️'
            ranking_color = '#ef4444'
            ranking_badge = 'danger'
        
        constructoras_data.append({
            'constructora': constructora,
            'total_observaciones': total_obs,
            'obs_resueltas': obs_resueltas,
            'obs_pendientes': obs_pendientes,
            'obs_alta_pendientes': obs_alta_pendientes,
            'tasa_resolucion': round(tasa_resolucion, 1),
            'score_total': round(score_total, 1),
            'score_resolucion': round(score_resolucion, 1),
            'score_calidad': round(score_calidad, 1),
            'score_eficiencia': round(score_eficiencia, 1),
            'ranking': ranking,
            'ranking_icon': ranking_icon,
            'ranking_color': ranking_color,
            'ranking_badge': ranking_badge,
            'total_proyectos': proyectos.count(),
        })
    
    # Ordenar por score (mayor score = mejor ranking)
    constructoras_data.sort(key=lambda x: x['score_total'], reverse=True)
    
    # Agregar posición en ranking
    for idx, data in enumerate(constructoras_data, start=1):
        data['posicion'] = idx
    
    # Calcular estadísticas globales
    total_observaciones_sistema = sum(c['total_observaciones'] for c in constructoras_data)
    promedio_tasa_resolucion = sum(c['tasa_resolucion'] for c in constructoras_data) / len(constructoras_data) if constructoras_data else 0
    mejor_constructora = constructoras_data[0] if constructoras_data else None
    
    # NUEVO: Calcular distribución de fallas por recinto (GENERAL)
    from django.db.models import Count
    distribucion_general = (
        RegistroPostventa.objects
        .values('recinto')
        .annotate(cantidad=Count('id'))
        .order_by('-cantidad')
    )
    
    # Preparar datos para gráfico de pastel general
    recintos_labels = [item['recinto'] for item in distribucion_general]
    recintos_counts = [item['cantidad'] for item in distribucion_general]
    
    # NUEVO: Añadir distribución por recinto para cada constructora
    for data in constructoras_data:
        constructora = data['constructora']
        proyectos = Proyecto.objects.filter(constructora=constructora)
        
        distribucion_constructora = (
            RegistroPostventa.objects
            .filter(proyecto__in=proyectos)
            .values('recinto')
            .annotate(cantidad=Count('id'))
            .order_by('-cantidad')
        )
        
        data['distribucion_recintos'] = list(distribucion_constructora)
    
    context = {
        'rol': request.user.perfil.rol,
        'constructoras_data': constructoras_data,
        'total_observaciones_sistema': total_observaciones_sistema,
        'promedio_tasa_resolucion': round(promedio_tasa_resolucion, 1),
        'mejor_constructora': mejor_constructora,
        'total_constructoras': len(constructoras_data),
        'recintos_labels': recintos_labels,
        'recintos_counts': recintos_counts,
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
            # Estado seguimiento por defecto cuando familia reporta
            registro.estado_seguimiento = 'EN_REVISION'  # Admin lo cambiará después
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
            
            # 🔔 NOTIFICACIÓN AUTOMÁTICA - Familia reportó observación
            # Notificar al trabajador asignado al proyecto
            trabajadores_notificados = 0
            if vivienda.proyecto:
                # Notificar trabajadores asignados a este proyecto
                trabajadores = PerfilUsuario.objects.filter(
                    rol='Trabajador',
                    proyecto_asignado=vivienda.proyecto
                )
                for trabajador in trabajadores:
                    crear_notificacion(
                        usuario=trabajador.user,
                        tipo='NUEVA_OBSERVACION',
                        titulo=f'Nueva observación reportada - {vivienda.proyecto.nombre}',
                        mensaje=f'Familia reportó problema en {registro.recinto}. Urgencia: {registro.get_urgencia_display()}',
                        url_destino=f'/fichas-inmuebles/{ficha.id}/'
                    )
                    trabajadores_notificados += 1
                
                # Notificar también a todos los administradores
                admins = PerfilUsuario.objects.filter(rol='Admin')
                for admin in admins:
                    crear_notificacion(
                        usuario=admin.user,
                        tipo='NUEVA_OBSERVACION',
                        titulo=f'Nueva observación - {vivienda.proyecto.nombre}',
                        mensaje=f'Familia reportó: {registro.observacion[:80]}...',
                        url_destino=f'/fichas-inmuebles/{ficha.id}/'
                    )
            
            # Mensaje de éxito
            mensaje = f"✅ Tu observación sobre '{registro.recinto}' ha sido registrada exitosamente."
            if evidencias_creadas > 0:
                mensaje += f" Se guardaron {evidencias_creadas} archivo(s) de evidencia."
            if trabajadores_notificados > 0:
                mensaje += f" Se notificó al equipo técnico."
            
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
    ).select_related('reportante').prefetch_related('evidencias').order_by('-creado_en')
    
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
    dias_postventa = ficha.dias_desde_entrega() if ficha.fecha_entrega else 0
    dias_restantes_ds49 = ficha.dias_restantes_ds49() if ficha.fecha_entrega else None
    estado_ds49 = ficha.estado_ds49()
    porcentaje_ds49 = ficha.porcentaje_ds49()
    
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
        'dias_restantes_ds49': dias_restantes_ds49,
        'estado_ds49': estado_ds49,
        'porcentaje_ds49': porcentaje_ds49,
    }
    
    return render(request, 'core/detalle_ficha_inmueble.html', context)


@login_required
def detalle_registro_postventa(request, registro_id):
    """Vista detallada de un registro de postventa accesible según rol."""
    from django.contrib import messages
    perfil = getattr(request.user, "perfil", None)
    rol = (perfil.rol if perfil else None) or ("Admin" if request.user.is_superuser else None)

    registro = get_object_or_404(
        RegistroPostventa.objects.select_related(
            "proyecto", "ficha__vivienda", "reportante"
        ).prefetch_related("evidencias__subido_por"),
        id=registro_id
    )

    ficha = registro.ficha
    vivienda = getattr(ficha, "vivienda", None)

    # Validar permisos por rol
    if rol == "Familia":
        vivienda_asignada = getattr(perfil, "vivienda_asignada", None)
        if not vivienda_asignada or not vivienda or vivienda_asignada.id != vivienda.id:
            messages.error(request, "No tienes permisos para ver este reporte.")
            return redirect("dashboard")
    elif rol == "Trabajador":
        proyecto_asignado = getattr(perfil, "proyecto_asignado", None)
        if not proyecto_asignado or proyecto_asignado.id != registro.proyecto_id:
            messages.error(request, "Este registro no pertenece a tu proyecto asignado.")
            return redirect("dashboard")
    elif rol == "Admin":
        pass
    else:
        messages.error(request, "No tienes permisos para ver este reporte.")
        return redirect("dashboard")

    propietario = None
    if vivienda:
        propietario = (
            PerfilUsuario.objects.select_related("user")
            .filter(vivienda_asignada=vivienda)
            .first()
        )

    evidencias = list(registro.evidencias.all())
    video_exts = (".mp4", ".mov", ".webm", ".ogg", ".mkv")
    for ev in evidencias:
        filename = ev.archivo.name.lower() if ev.archivo else ""
        ev.is_video = filename.endswith(video_exts)

    comentarios = registro.comentarios.select_related("autor").all()
    comentario_form = RegistroComentarioForm() if rol in ("Admin", "Trabajador") else None

    context = {
        "registro": registro,
        "vivienda": vivienda,
        "ficha": ficha,
        "proyecto": registro.proyecto,
        "evidencias": evidencias,
        "propietario": propietario,
        "rol": rol,
        "puede_gestionar": rol in ("Admin", "Trabajador"),
        "estados": ESTADOS,
        "comentarios": comentarios,
        "comentario_form": comentario_form,
    }
    return render(request, "core/detalle_registro_postventa.html", context)


@login_required
@require_POST
def actualizar_fecha_entrega(request, ficha_id):
    """Actualiza la fecha de entrega de una ficha de inmueble"""
    ficha = get_object_or_404(FichaInmueble, id=ficha_id)
    
    # Verificar permisos
    try:
        perfil = request.user.perfil
        rol = perfil.rol if hasattr(perfil, 'rol') else None
    except:
        return JsonResponse({'error': 'No se pudo obtener el perfil del usuario'}, status=400)
    
    if rol not in ["Admin", "Trabajador"]:
        return JsonResponse({'error': 'No tienes permisos para realizar esta acción'}, status=403)
    
    if rol == "Trabajador" and hasattr(perfil, 'proyecto_asignado'):
        if ficha.proyecto != perfil.proyecto_asignado:
            return JsonResponse({'error': 'No tienes permisos para editar esta ficha'}, status=403)
    
    # Obtener la fecha del request
    fecha_entrega = request.POST.get('fecha_entrega')
    
    if not fecha_entrega:
        return JsonResponse({'error': 'Debe proporcionar una fecha de entrega'}, status=400)
    
    try:
        from datetime import datetime
        ficha.fecha_entrega = datetime.strptime(fecha_entrega, '%Y-%m-%d').date()
        ficha.save()
        
        messages.success(request, f'Fecha de entrega actualizada correctamente a {ficha.fecha_entrega.strftime("%d/%m/%Y")}')
        
        return JsonResponse({
            'success': True,
            'fecha_entrega': ficha.fecha_entrega.strftime('%Y-%m-%d'),
            'dias_desde_entrega': ficha.dias_desde_entrega(),
            'dias_restantes_ds49': ficha.dias_restantes_ds49(),
            'estado_ds49': ficha.estado_ds49(),
            'porcentaje_ds49': ficha.porcentaje_ds49(),
        })
    except ValueError:
        return JsonResponse({'error': 'Formato de fecha inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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


# =============================================================================
# ASIGNACIÓN DE TRABAJADORES A PROYECTOS
# =============================================================================

@login_required
@require_role("Admin")
def asignar_trabajadores_proyecto(request):
    """Vista para que Admin asigne trabajadores a proyectos"""
    perfil = request.user.perfil
    
    # Obtener todos los proyectos y trabajadores
    proyectos = Proyecto.objects.all().order_by('codigo')
    trabajadores = PerfilUsuario.objects.filter(rol="Trabajador").select_related('user', 'proyecto_asignado')
    
    if request.method == "POST":
        trabajador_id = request.POST.get('trabajador_id')
        proyecto_id = request.POST.get('proyecto_id')
        accion = request.POST.get('accion')
        
        try:
            trabajador = PerfilUsuario.objects.get(id=trabajador_id, rol="Trabajador")
            
            if accion == 'asignar' and proyecto_id:
                proyecto = Proyecto.objects.get(id=proyecto_id)
                trabajador.proyecto_asignado = proyecto
                trabajador.save()
                messages.success(request, f'✅ {trabajador.get_nombre_completo()} asignado al proyecto {proyecto.codigo}')
            elif accion == 'desasignar':
                proyecto_anterior = trabajador.proyecto_asignado
                trabajador.proyecto_asignado = None
                trabajador.save()
                messages.success(request, f'✅ {trabajador.get_nombre_completo()} removido del proyecto {proyecto_anterior.codigo if proyecto_anterior else ""}')
                
            return redirect('asignar_trabajadores_proyecto')
        except Exception as e:
            messages.error(request, f'❌ Error: {str(e)}')
            return redirect('asignar_trabajadores_proyecto')
    
    context = {
        'rol': perfil.rol,
        'proyectos': proyectos,
        'trabajadores': trabajadores,
        'trabajadores_sin_proyecto': trabajadores.filter(proyecto_asignado__isnull=True),
        'trabajadores_con_proyecto': trabajadores.filter(proyecto_asignado__isnull=False),
    }
    
    return render(request, 'core/asignar_trabajadores_proyecto.html', context)


# =============================================================================
# REPORTAR OBSERVACIONES - TRABAJADOR
# =============================================================================

@login_required
@require_role("Trabajador")
def reportar_observacion_trabajador(request):
    """Vista para que los trabajadores reporten observaciones"""
    from .forms import ObservacionFamiliaForm
    
    perfil = request.user.perfil
    
    # Verificar que el trabajador tenga proyecto asignado
    if not perfil.proyecto_asignado:
        messages.error(request, "Aún no tienes un proyecto asignado. Contacta con el administrador.")
        return redirect("dashboard")
    
    proyecto = perfil.proyecto_asignado
    
    # Obtener todas las viviendas del proyecto
    viviendas = Vivienda.objects.filter(proyecto=proyecto).order_by('numero')
    
    if request.method == "POST":
        form = ObservacionFamiliaForm(request.POST, request.FILES)
        vivienda_id = request.POST.get('vivienda_id')
        
        if not vivienda_id:
            messages.error(request, "Debes seleccionar una vivienda")
            return redirect('reportar_observacion_trabajador')
        
        try:
            vivienda = Vivienda.objects.get(id=vivienda_id, proyecto=proyecto)
        except Vivienda.DoesNotExist:
            messages.error(request, "Vivienda no encontrada en tu proyecto")
            return redirect('reportar_observacion_trabajador')
        
        if form.is_valid():
            # Obtener o crear la ficha de inmueble
            ficha, created = FichaInmueble.objects.get_or_create(
                proyecto=proyecto,
                vivienda=vivienda
            )
            
            # Crear el registro de observación
            registro = form.save(commit=False)
            registro.proyecto = proyecto
            registro.ficha = ficha
            registro.reportante = request.user
            registro.save()
            
            # Procesar evidencias (archivos múltiples - fotos y videos)
            archivos = request.FILES.getlist('evidencias')
            evidencias_creadas = 0
            
            for archivo in archivos[:10]:  # Máximo 10 archivos
                if archivo.size <= 50 * 1024 * 1024:  # Máximo 50 MB por archivo (para videos)
                    Evidencia.objects.create(
                        registro=registro,
                        archivo=archivo,
                        comentario=f"Evidencia subida por {request.user.username} (Trabajador)",
                        subido_por=request.user
                    )
                    evidencias_creadas += 1
            
            # Mensaje de éxito
            mensaje = f"✅ Tu observación sobre '{registro.recinto}' en {vivienda} ha sido registrada exitosamente."
            if evidencias_creadas > 0:
                mensaje += f" Se guardaron {evidencias_creadas} archivo(s) de evidencia."
            
            messages.success(request, mensaje)
            return redirect("dashboard")
    else:
        form = ObservacionFamiliaForm()
    
    context = {
        'rol': perfil.rol,
        'form': form,
        'proyecto': proyecto,
        'viviendas': viviendas,
    }
    
    return render(request, "core/reportar_observacion_trabajador.html", context)


# ==================== NOTIFICACIONES ====================

@login_required
def notificaciones_list(request):
    """Vista del historial completo de notificaciones del usuario actual"""
    # Obtener todas las notificaciones del usuario
    notificaciones = Notificacion.objects.filter(usuario=request.user)
    
    # Filtrar por estado si se especifica
    filtro = request.GET.get('filtro', 'todas')
    if filtro == 'no_leidas':
        notificaciones = notificaciones.filter(leida=False)
    elif filtro == 'leidas':
        notificaciones = notificaciones.filter(leida=True)
    
    # Paginación
    from django.core.paginator import Paginator
    paginator = Paginator(notificaciones, 20)  # 20 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Contador de no leídas
    no_leidas_count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
    
    context = {
        'page_obj': page_obj,
        'filtro_actual': filtro,
        'no_leidas_count': no_leidas_count,
    }
    
    return render(request, 'core/notificaciones_list.html', context)


@login_required
@require_POST
def marcar_notificacion_leida(request, notif_id):
    """Vista AJAX para marcar una notificación como leída"""
    try:
        notificacion = Notificacion.objects.get(id=notif_id, usuario=request.user)
        notificacion.marcar_leida()
        
        # Contador actualizado
        no_leidas_count = Notificacion.objects.filter(usuario=request.user, leida=False).count()
        
        return JsonResponse({
            'success': True,
            'no_leidas_count': no_leidas_count
        })
    except Notificacion.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Notificación no encontrada'
        }, status=404)


def crear_notificacion(usuario, tipo, titulo, mensaje, url_destino):
    """Helper function para crear una notificación"""
    Notificacion.objects.create(
        usuario=usuario,
        tipo=tipo,
        titulo=titulo,
        mensaje=mensaje,
        url_destino=url_destino
    )