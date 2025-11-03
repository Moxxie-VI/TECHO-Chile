from django.contrib import admin
from .models import (
    Privilegio,
    Proyecto,
    Trabajador,
    Cliente,
    RegistroPosventa,
    EstadoInmueble,
)

@admin.register(Privilegio)
class PrivilegioAdmin(admin.ModelAdmin):
    list_display = ("id", "tipoPrivilegio")
    search_fields = ("tipoPrivilegio",)

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ("id", "codigoProyecto", "nomProyecto", "ubicacion", "fechaInicio", "fechaEstiTermi")
    search_fields = ("codigoProyecto", "nomProyecto", "ubicacion")

@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ("id", "rutTrabajador", "nombreTrab", "apellidoTrab", "correo", "privilegio", "proyecto")
    search_fields = ("rutTrabajador", "nombreTrab", "apellidoTrab", "correo")
    list_filter = ("privilegio", "proyecto")

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("id", "rutCliente", "nombreCli", "apellidoCli", "correo", "telefono")
    search_fields = ("rutCliente", "nombreCli", "apellidoCli", "correo")

@admin.register(RegistroPosventa)
class RegistroPosventaAdmin(admin.ModelAdmin):
    list_display = ("id", "tipoCatastro", "proyecto", "fechaCreacion")
    search_fields = ("tipoCatastro", "observacion")
    list_filter = ("tipoCatastro", "proyecto")
    readonly_fields = ("fechaCreacion",)

@admin.register(EstadoInmueble)
class EstadoInmuebleAdmin(admin.ModelAdmin):
    list_display = ("id", "folioInmueble", "estado", "fechaActualizacion")
    search_fields = ("folioInmueble", "estado")
    list_filter = ("estado",)
    readonly_fields = ("fechaActualizacion",)


