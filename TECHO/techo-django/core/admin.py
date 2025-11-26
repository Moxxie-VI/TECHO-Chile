from django.contrib import admin
from .models import Privilegio, Constructora, Proyecto, Vivienda, FichaInmueble, EstadoInmueble, RegistroPostventa, RegistroComentario, Evidencia, Reporte, PerfilUsuario
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PerfilUsuario
from django.contrib.auth.models import User


admin.site.register(Privilegio)
admin.site.register(Constructora)
admin.site.register(Proyecto)
admin.site.register(Vivienda)
admin.site.register(FichaInmueble)
admin.site.register(EstadoInmueble)
admin.site.register(RegistroPostventa)
admin.site.register(RegistroComentario)
admin.site.register(Evidencia)
admin.site.register(Reporte)

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Signal que crea automáticamente un perfil cuando se crea un usuario.
    Usa get_or_create para evitar duplicados.
    """
    if created:
        rol = "Admin" if instance.is_superuser else "Trabajador"
        PerfilUsuario.objects.get_or_create(
            user=instance,
            defaults={'rol': rol}
        )
