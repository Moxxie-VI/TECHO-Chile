import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from core.models import PerfilUsuario, Proyecto

# Admin
u1, created = User.objects.get_or_create(username="admin@techo.cl", email="admin@techo.cl", is_staff=True, is_superuser=True)
if created or not hasattr(u1, 'perfil'):
    u1.set_password("Admin#2025")
    u1.save()
    perfil1, _ = PerfilUsuario.objects.get_or_create(user=u1, defaults={'rol': 'Admin'})
    if perfil1.rol != 'Admin':
        perfil1.rol = 'Admin'
        perfil1.save()
    print("Usuario Admin creado/actualizado: admin@techo.cl")
else:
    print("Usuario Admin ya existe: admin@techo.cl")

# Trabajador
u2, created = User.objects.get_or_create(username="trabajador@techo.cl", email="trabajador@techo.cl", is_staff=True)
if created or not hasattr(u2, 'perfil'):
    u2.set_password("Trabajador#2025")
    u2.save()
    perfil2, _ = PerfilUsuario.objects.get_or_create(user=u2, defaults={'rol': 'Trabajador'})
    if perfil2.rol != 'Trabajador':
        perfil2.rol = 'Trabajador'
        perfil2.save()
    print("Usuario Trabajador creado/actualizado: trabajador@techo.cl")
else:
    print("Usuario Trabajador ya existe: trabajador@techo.cl")

# Familia
u3, created = User.objects.get_or_create(username="familia@techo.cl", email="familia@techo.cl")
if created or not hasattr(u3, 'perfil'):
    u3.set_password("Familia#2025")
    u3.save()
    perfil3, _ = PerfilUsuario.objects.get_or_create(user=u3, defaults={'rol': 'Familia'})
    if perfil3.rol != 'Familia':
        perfil3.rol = 'Familia'
        perfil3.save()
    print("Usuario Familia creado/actualizado: familia@techo.cl")
else:
    print("Usuario Familia ya existe: familia@techo.cl")

print("\nProceso de creacion de usuarios completado!")

