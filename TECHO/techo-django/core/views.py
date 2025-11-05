from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from accounts.decorators import require_role
from django.http import HttpResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.mail import EmailMessage
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

    registros = (RegistroPostventa.objects
                 .filter(proyecto=proyecto)
                 .order_by("-creado_en")[:200])
    stats = {
        "viviendas": Vivienda.objects.filter(proyecto=proyecto).count(),
        "registros": registros.count(),
        "urgentes": registros.filter(urgencia="ALTA").count(),
    }

    ctx = {
        "proyecto": proyecto,
        "registros": registros,
        "stats": stats,
        "generado_en": timezone.localtime(),
    }

    pdf_bytes = render_to_pdf("reports/proyecto_pdf.html", ctx)
    if not pdf_bytes:
        return HttpResponseBadRequest("No se pudo generar PDF")

    filename = f"reporte_{proyecto.codigo}.pdf"
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

    registros = (RegistroPostventa.objects
                 .filter(proyecto=proyecto)
                 .order_by("-creado_en")[:200])
    stats = {
        "viviendas": Vivienda.objects.filter(proyecto=proyecto).count(),
        "registros": registros.count(),
        "urgentes": registros.filter(urgencia="ALTA").count(),
    }

    ctx = {
        "proyecto": proyecto,
        "registros": registros,
        "stats": stats,
        "generado_en": timezone.localtime(),
    }

    pdf_bytes = render_to_pdf("reports/proyecto_pdf.html", ctx)
    if not pdf_bytes:
        return HttpResponseBadRequest("No se pudo generar PDF")

    # Enviar email (por ahora usa console backend si así está en settings)
    subject = f"Reporte Proyecto {proyecto.codigo} — {proyecto.nombre}"
    body = "Adjunto reporte PDF generado desde la plataforma TECHO."
    email = EmailMessage(subject=subject, body=body, to=[to_addr])
    email.attach(filename=f"reporte_{proyecto.codigo}.pdf", content=pdf_bytes, mimetype="application/pdf")
    email.send(fail_silently=False)

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