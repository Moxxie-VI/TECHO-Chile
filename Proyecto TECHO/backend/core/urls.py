from django.contrib import admin
from django.urls import path, include
from .views import (
    view_landing,
    view_login,
    view_recuperar,
    view_panel_trabajador,
    view_panel_admin,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # API backend (lo que ya tenías)
    path("api/", include("api.urls")),

    # Páginas públicas / frontend
    path("", view_landing, name="landing"),
    path("login/", view_login, name="login"),
    path("recuperar/", view_recuperar, name="recuperar"),

    # Paneles internos según tipo de usuario
    path("panel/trabajador/", view_panel_trabajador, name="panel_trabajador"),
    path("panel/admin/", view_panel_admin, name="panel_admin"),
]


