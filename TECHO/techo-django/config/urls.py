from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    home, viviendas_list, proyectos_list, reportes_home, 
    reporte_proyecto_pdf, reporte_proyecto_enviar,
    admin_proyectos, admin_proyecto_form, admin_proyecto_delete, 
    subir_evidencia, cambiar_estado_registro,
    monitoreo_ds49, actualizar_fecha_entrega,
    admin_viviendas, crear_vivienda, editar_vivienda, eliminar_vivienda,
    admin_constructoras, crear_constructora, editar_constructora, eliminar_constructora,
    reportar_observacion_familia, buscar_familia_por_rut,
    fichas_inmuebles, detalle_ficha_inmueble, buscar_usuario_por_rut
)
from accounts.views import (
    login_view, logout_view, dashboard, perfil, ayuda, tutorial, 
    crear_usuario, listar_usuarios, editar_usuario, eliminar_usuario,
    recuperar_password_solicitar, recuperar_password_verificar
)

urlpatterns = [
    path("", home, name="home"),
    path("admin/", admin.site.urls),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("recuperar-password/", recuperar_password_solicitar, name="recuperar_password_solicitar"),
    path("recuperar-password/verificar/", recuperar_password_verificar, name="recuperar_password_verificar"),
    path("dashboard/", dashboard, name="dashboard"),
    path("viviendas/", viviendas_list, name="viviendas_list"),
    path("proyectos/", proyectos_list, name="proyectos_list"),
    path("reportes/", reportes_home, name="reportes_home"),
    path("reportes/proyecto/pdf/", reporte_proyecto_pdf, name="reporte_proyecto_pdf"),
    path("reportes/proyecto/enviar/", reporte_proyecto_enviar, name="reporte_proyecto_enviar"),
    path("panel/admin/proyectos/", admin_proyectos, name="admin_proyectos"),
    path("panel/admin/proyectos/form/", admin_proyecto_form, name="admin_proyecto_new"),
    path("panel/admin/proyectos/form/<int:pk>/", admin_proyecto_form, name="admin_proyecto_edit"),
    path("panel/admin/proyectos/delete/<int:pk>/", admin_proyecto_delete, name="admin_proyecto_delete"),
    path("perfil/", perfil, name="perfil"),
    path("ayuda/", ayuda, name="ayuda"),
    path("tutorial/", tutorial, name="tutorial"),
    path("usuarios/", listar_usuarios, name="listar_usuarios"),
    path("usuarios/crear/", crear_usuario, name="crear_usuario"),
    path("usuarios/editar/<int:user_id>/", editar_usuario, name="editar_usuario"),
    path("usuarios/eliminar/<int:user_id>/", eliminar_usuario, name="eliminar_usuario"),
    path("trabajo/registro/<int:reg_id>/evidencia/", subir_evidencia, name="subir_evidencia"),
    path("trabajo/registro/<int:reg_id>/estado/", cambiar_estado_registro, name="cambiar_estado_registro"),
    # Sistema DS 49
    path("ds49/monitoreo/", monitoreo_ds49, name="monitoreo_ds49"),
    path("ds49/actualizar-fecha/<int:ficha_id>/", actualizar_fecha_entrega, name="actualizar_fecha_entrega"),
    # Gestión de Viviendas
    path("panel/admin/viviendas/", admin_viviendas, name="admin_viviendas"),
    path("panel/admin/viviendas/crear/", crear_vivienda, name="crear_vivienda"),
    path("panel/admin/viviendas/editar/<int:vivienda_id>/", editar_vivienda, name="editar_vivienda"),
    path("panel/admin/viviendas/eliminar/<int:vivienda_id>/", eliminar_vivienda, name="eliminar_vivienda"),
    # Gestión de Constructoras
    path("panel/admin/constructoras/", admin_constructoras, name="admin_constructoras"),
    path("panel/admin/constructoras/crear/", crear_constructora, name="crear_constructora"),
    path("panel/admin/constructoras/editar/<int:constructora_id>/", editar_constructora, name="editar_constructora"),
    path("panel/admin/constructoras/eliminar/<int:constructora_id>/", eliminar_constructora, name="eliminar_constructora"),
    # Familias - Reportar observaciones
    path("familia/reportar-observacion/", reportar_observacion_familia, name="reportar_observacion_familia"),
    # Admin - Asignación de viviendas por RUT
    path("panel/admin/asignar-vivienda-rut/", buscar_familia_por_rut, name="buscar_familia_por_rut"),
    # Fichas de Inmuebles - Ver observaciones
    path("fichas-inmuebles/", fichas_inmuebles, name="fichas_inmuebles"),
    path("fichas-inmuebles/<int:ficha_id>/", detalle_ficha_inmueble, name="detalle_ficha_inmueble"),
    # API - Buscar usuario por RUT
    path("api/buscar-usuario-rut/", buscar_usuario_por_rut, name="buscar_usuario_por_rut"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


