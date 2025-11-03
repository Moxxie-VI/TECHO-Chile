# 🏠 Plataforma de Gestión Habitacional — TECHO Chile

**Proyecto académico y social desarrollado para TECHO-Chile**, enfocado en la **gestión y seguimiento postventa de viviendas** bajo el programa **DS49 del MINVU**.  
La plataforma permite a administradores, trabajadores y familias gestionar información habitacional, evidencias y reportes, de forma **segura, accesible y visualmente amigable**.

---

##  Características principales

-  Interfaz moderna con **tema claro/oscuro** y controles de accesibilidad (tamaño de letra, contraste).  
-  **Tres roles principales**:
  - **Admin:** crea, edita o elimina proyectos, usuarios y reportes.
  - **Trabajador:** gestiona viviendas asignadas, sube evidencias y reporta avances.
  - **Familia:** visualiza el estado de su vivienda y observaciones postventa.
-  Importación automática de datos desde planillas Excel (proporcionadas por TECHO).
-  Arquitectura modular (Django + PostgreSQL + Bootstrap + HTMX).
-  Totalmente escalable y compatible con despliegue en Render, Railway u otros servicios cloud.

---

##  Requisitos

| Requisito | Versión recomendada |
|------------|--------------------|
| Python | 3.10 – 3.13 |
| PostgreSQL | 14+ |
| pgAdmin4 | (para administrar la BD) |
| GitHub Desktop o Git | Última versión |

---

##  Instalación (desde cualquier PC)

### 1, Clonar el repositorio

Con **GitHub Desktop:**

### 2. Crear entorno virtual

python -m venv venv
venv\Scripts\activate   # (Windows)
|
source venv/bin/activate  # (Linux/Mac)

### 3. Instalar dependencias

pip install -r requirements.txt

### 4. Configurar variables de entorno
Crea un archivo llamado .env dentro de la carpeta config/ con el siguiente contenido:

SECRET_KEY=techo-secret-key
DEBUG=True
DB_NAME=techo
DB_USER=postgres
DB_PASSWORD=tu_contraseña
DB_HOST=localhost
DB_PORT=5432
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

Cambia DB_PASSWORD por tu contraseña real de PostgreSQL.

### 5. Crear base de datos en PostgreSQL

Desde pgAdmin4:

Clic derecho → Create Database → Nombre: techo

Guardar.

### 6. Migrar modelos a la base

python manage.py makemigrations
python manage.py migrate

### 7. Cargar datos de ejemplo (opcional)

python manage.py import_excel --file "C:\ruta\a\ejemplo.xlsx"

### 8. Crear usuarios de prueba

python manage.py shell

from django.contrib.auth.models import User
from core.models import PerfilUsuario, Proyecto

# Admin
u1, _ = User.objects.get_or_create(username="admin@techo.cl", email="admin@techo.cl", is_staff=True, is_superuser=True)
u1.set_password("Admin#2025"); u1.save()
PerfilUsuario.objects.get_or_create(user=u1, rol="Admin")

# Trabajador
u2, _ = User.objects.get_or_create(username="trabajador@techo.cl", email="trabajador@techo.cl", is_staff=True)
u2.set_password("Trabajador#2025"); u2.save()
PerfilUsuario.objects.get_or_create(user=u2, rol="Trabajador")

# Familia
u3, _ = User.objects.get_or_create(username="familia@techo.cl", email="familia@techo.cl")
u3.set_password("Familia#2025"); u3.save()
PerfilUsuario.objects.get_or_create(user=u3, rol="Familia")

exit()

### 9. Iniciar el servidor

python manage.py runserver

## Credenciales

| Rol        | Usuario                                           | Contraseña      |
| ---------- | ------------------------------------------------- | --------------- |
| Admin      | [admin@techo.cl](mailto:admin@techo.cl)           | Admin#2025      |
| Trabajador | [trabajador@techo.cl](mailto:trabajador@techo.cl) | Trabajador#2025 |
| Familia    | [familia@techo.cl](mailto:familia@techo.cl)       | Familia#2025    |


Proyecto académico — Uso educativo.
© 2025 TECHO Chile · Todos los derechos reservados.
