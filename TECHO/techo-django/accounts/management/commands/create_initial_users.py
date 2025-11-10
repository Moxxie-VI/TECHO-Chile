"""
Comando para crear usuarios iniciales automáticamente
Se ejecuta durante el deploy en Render
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import PerfilUsuario


class Command(BaseCommand):
    help = 'Crea usuarios iniciales si no existen (Admin, Trabajador, Familia)'

    def handle(self, *args, **kwargs):
        self.stdout.write("🔍 Verificando usuarios iniciales...")
        
        usuarios_creados = 0
        
        # ============================================================
        # USUARIO ADMINISTRADOR
        # ============================================================
        if not User.objects.filter(username='admin@techo.cl').exists():
            self.stdout.write("📝 Creando usuario Admin...")
            admin = User.objects.create_superuser(
                username='admin@techo.cl',
                email='admin@techo.cl',
                password='Admin#2025',
                first_name='Administrador',
                last_name='TECHO'
            )
            # Actualizar perfil
            perfil = PerfilUsuario.objects.get(user=admin)
            perfil.rol = 'Admin'
            perfil.nombre = 'Administrador'
            perfil.apellido = 'TECHO'
            perfil.correo_personal = 'admin@techo.cl'
            perfil.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Usuario Admin creado: admin@techo.cl / Admin#2025'))
            usuarios_creados += 1
        else:
            self.stdout.write("✓ Usuario Admin ya existe")

        # ============================================================
        # USUARIO TRABAJADOR (Ejemplo)
        # ============================================================
        if not User.objects.filter(username='trabajador@techo.cl').exists():
            self.stdout.write("📝 Creando usuario Trabajador de prueba...")
            trabajador = User.objects.create_user(
                username='trabajador@techo.cl',
                email='trabajador@techo.cl',
                password='Trabajador#2025',
                first_name='Juan',
                last_name='Pérez'
            )
            # Actualizar perfil
            perfil = PerfilUsuario.objects.get(user=trabajador)
            perfil.rol = 'Trabajador'
            perfil.nombre = 'Juan'
            perfil.apellido = 'Pérez'
            perfil.correo_personal = 'trabajador@techo.cl'
            perfil.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Usuario Trabajador creado: trabajador@techo.cl / Trabajador#2025'))
            usuarios_creados += 1
        else:
            self.stdout.write("✓ Usuario Trabajador ya existe")

        # ============================================================
        # USUARIO FAMILIA (Ejemplo)
        # ============================================================
        if not User.objects.filter(username='familia@techo.cl').exists():
            self.stdout.write("📝 Creando usuario Familia de prueba...")
            familia = User.objects.create_user(
                username='familia@techo.cl',
                email='familia@techo.cl',
                password='Familia#2025',
                first_name='María',
                last_name='González'
            )
            # Actualizar perfil
            perfil = PerfilUsuario.objects.get(user=familia)
            perfil.rol = 'Familia'
            perfil.nombre = 'María'
            perfil.apellido = 'González'
            perfil.correo_personal = 'familia@techo.cl'
            perfil.save()
            
            self.stdout.write(self.style.SUCCESS('✅ Usuario Familia creado: familia@techo.cl / Familia#2025'))
            usuarios_creados += 1
        else:
            self.stdout.write("✓ Usuario Familia ya existe")

        # ============================================================
        # RESUMEN
        # ============================================================
        if usuarios_creados > 0:
            self.stdout.write(self.style.SUCCESS(f'\n🎉 {usuarios_creados} usuario(s) creado(s) exitosamente!'))
            self.stdout.write('\n📋 CREDENCIALES DE ACCESO:')
            self.stdout.write('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━')
            self.stdout.write('👤 Admin:      admin@techo.cl / Admin#2025')
            self.stdout.write('👷 Trabajador: trabajador@techo.cl / Trabajador#2025')
            self.stdout.write('🏠 Familia:    familia@techo.cl / Familia#2025')
            self.stdout.write('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n')
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ Todos los usuarios ya existen. No se creó ninguno nuevo.\n'))

