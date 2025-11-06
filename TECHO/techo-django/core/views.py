from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import require_role
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import EmailMessage
from django.db.models import Count
from .forms import ProyectoForm, ViviendaForm, RegistroPostventaForm, EvidenciaForm
from .models import Proyecto, Vivienda, RegistroPostventa, Evidencia, ESTADOS
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