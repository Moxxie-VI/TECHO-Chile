from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    home, viviendas_list, proyectos_list, reportes_home, 
    reporte_proyecto_pdf, reporte_proyecto_enviar,
    admin_proyectos, admin_proyecto_form, admin_proyecto_delete, 
    subir_evidencia, cambiar_estado_registro
)
from accounts.views import (
    login_view, logout_view, dashboard, perfil, ayuda, tutorial, crear_usuario,
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
    path("usuarios/crear/", crear_usuario, name="crear_usuario"),
    path("trabajo/registro/<int:reg_id>/evidencia/", subir_evidencia, name="subir_evidencia"),
    path("trabajo/registro/<int:reg_id>/estado/", cambiar_estado_registro, name="cambiar_estado_registro"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


