# ✅ CHECKLIST PARA PRODUCCIÓN - TECHO Chile

## 📋 Tareas Críticas Antes de Deploy

### 1. ⚡ URGENTE: Configurar Servicio de Email

#### Opción A: SendGrid (Recomendado)
- [ ] Crear cuenta en [SendGrid](https://sendgrid.com)
- [ ] Obtener API Key
- [ ] Configurar variables de entorno en el servidor:
  ```bash
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  EMAIL_HOST=smtp.sendgrid.net
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  EMAIL_HOST_USER=apikey
  EMAIL_HOST_PASSWORD=<tu-sendgrid-api-key>
  DEFAULT_FROM_EMAIL=proyecto.techochile@gmail.com
  ```
- [ ] Verificar dominio en SendGrid
- [ ] Probar envío de correos

#### Opción B: Gmail SMTP
- [ ] Crear contraseña de aplicación en Gmail
- [ ] Configurar variables de entorno:
  ```bash
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
  EMAIL_HOST=smtp.gmail.com
  EMAIL_PORT=587
  EMAIL_USE_TLS=True
  EMAIL_HOST_USER=proyecto.techochile@gmail.com
  EMAIL_HOST_PASSWORD=<contraseña-de-aplicación>
  DEFAULT_FROM_EMAIL=proyecto.techochile@gmail.com
  ```

---

### 2. 🗄️ Base de Datos

- [x] Migraciones aplicadas localmente
- [ ] Verificar migraciones en producción
- [ ] Backup de base de datos antes de migrar
- [ ] Ejecutar en producción:
  ```bash
  python manage.py makemigrations
  python manage.py migrate
  ```

---

### 3. 🔒 Seguridad

- [ ] Cambiar `SECRET_KEY` en producción
- [ ] Configurar `ALLOWED_HOSTS`
- [ ] `DEBUG = False` en producción
- [ ] Configurar HTTPS
- [ ] Verificar que los códigos de recuperación NO se muestran en pantalla

---

### 4. 📦 Archivos Estáticos y Media

- [ ] Configurar almacenamiento de archivos media (AWS S3, etc.)
- [ ] Ejecutar `python manage.py collectstatic`
- [ ] Verificar permisos de carpeta `media/`
- [ ] Configurar límites de tamaño de archivo en el servidor

---

### 5. 🧪 Pruebas Funcionales

#### Recuperación de Contraseña:
- [ ] Solicitar código de recuperación
- [ ] Verificar que el correo llegue
- [ ] Confirmar que el código NO aparece en pantalla
- [ ] Probar cambio de contraseña

#### Perfiles de Usuario:
- [ ] Crear usuario con RUT válido
- [ ] Editar perfil con todos los campos nuevos
- [ ] Verificar formato de RUT (12.345.678-9)
- [ ] Probar subida de avatar

#### Viviendas:
- [ ] Crear vivienda con dirección completa
- [ ] Asignar vivienda por RUT
- [ ] Verificar búsqueda de familia por RUT funcione

#### Observaciones (Familias):
- [ ] Reportar observación desde dashboard familia
- [ ] Subir múltiples evidencias (fotos)
- [ ] Verificar que admin vea la observación
- [ ] Verificar que trabajador vea la observación (si está en el proyecto)

#### Tutorial Interactivo:
- [ ] Iniciar tutorial en dashboard familia
- [ ] Verificar animaciones funcionan correctamente
- [ ] Comprobar que se pueda saltar y reiniciar

#### Eliminación Segura:
- [ ] Intentar eliminar usuario sin texto de confirmación (debe fallar)
- [ ] Eliminar con texto correcto: "acepto eliminar usuario"
- [ ] Repetir para viviendas y constructoras

---

### 6. 📱 Compatibilidad

- [ ] Probar en Chrome
- [ ] Probar en Firefox
- [ ] Probar en Safari
- [ ] Probar en móviles (responsive)
- [ ] Probar modo oscuro

---

### 7. 📊 Monitoreo

- [ ] Configurar logs de errores
- [ ] Configurar alertas de email fallidos
- [ ] Monitorear uso de disco (carpeta media)

---

## 🎯 Post-Deploy Inmediato

1. [ ] Verificar que el sitio carga correctamente
2. [ ] Probar login con usuario existente
3. [ ] Enviar correo de prueba (recuperación de contraseña)
4. [ ] Crear un reporte de prueba como familia
5. [ ] Verificar que los reportes aparecen en admin/trabajador

---

## 📝 Notas Importantes

### RUT Chileno:
- El sistema valida automáticamente el formato y dígito verificador
- Formato aceptado: `12.345.678-9` o `12345678-9`
- Se almacena sin puntos ni guiones en la BD

### Observaciones:
- Máximo 5 archivos por observación
- Máximo 10 MB por archivo
- Formatos aceptados: imágenes y videos

### Tutorial:
- Se muestra automáticamente la primera vez
- Se puede saltar con "Saltar Tutorial"
- Se puede reiniciar con el botón "Ver Tutorial"

---

## 🆘 En Caso de Problemas

### Email no llega:
1. Verificar configuración SMTP
2. Revisar logs de Django
3. Probar con `python manage.py shell` + `send_mail()`
4. Verificar que SendGrid/Gmail no bloquee el dominio

### Migraciones fallan:
1. Hacer backup de la BD
2. Revisar `python manage.py showmigrations`
3. Aplicar migraciones una por una
4. Contactar al desarrollador si persiste

### Archivos no suben:
1. Verificar permisos de carpeta `media/`
2. Verificar límite de tamaño en servidor web (nginx/apache)
3. Revisar `settings.MEDIA_ROOT` y `MEDIA_URL`

---

## ✅ Checklist de Verificación Final

Antes de considerar el deploy completo:

- [ ] ✉️ Emails funcionan (recuperación de contraseña)
- [ ] 👤 Perfiles con RUT se crean correctamente
- [ ] 🏠 Viviendas se asignan por RUT
- [ ] 📝 Observaciones se crean y visualizan
- [ ] 🎨 Tutorial interactivo funciona
- [ ] 🗑️ Eliminaciones requieren confirmación
- [ ] 📱 Sitio es responsive
- [ ] 🔒 Seguridad configurada (HTTPS, DEBUG=False)

---

**Fecha de Última Actualización:** Noviembre 2025  
**Desarrollado para:** TECHO Chile

