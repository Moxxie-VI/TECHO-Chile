from django.contrib import admin
from .models import PlataformaUser

@admin.register(PlataformaUser)
class PlataformaUserAdmin(admin.ModelAdmin):
    list_display = ("nombre", "apellido", "correo", "rol", "estado", "creado_en")
    search_fields = ("nombre", "apellido", "correo", "rut")
    list_filter = ("rol", "estado")
    readonly_fields = ("creado_en",)

