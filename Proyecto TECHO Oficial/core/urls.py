from django.contrib import admin
from django.urls import path
from api.views import (
    landing_view,
    login_view,
    logout_view,
    dashboard_admin,
    dashboard_trabajador,
    dashboard_familia,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # público
    path("", landing_view, name="landing"),

    # auth
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # dashboards según rol
    path("panel/admin/", dashboard_admin, name="dashboard_admin"),
    path("panel/trabajador/", dashboard_trabajador, name="dashboard_trabajador"),
    path("panel/familia/", dashboard_familia, name="dashboard_familia"),
]



