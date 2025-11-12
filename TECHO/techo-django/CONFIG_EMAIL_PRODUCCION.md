# Configuración de Correos Electrónicos en Producción

## 🚨 IMPORTANTE - Seguridad Arreglada

**PROBLEMA CRÍTICO RESUELTO**: El sistema YA NO muestra códigos de recuperación en pantalla.  
Ahora los códigos solo se envían por correo electrónico de forma segura.

---

## 📧 Opción 1: SendGrid (RECOMENDADO para Render)

SendGrid es gratuito hasta 100 correos/día y funciona perfectamente en Render.

### Paso 1: Crear cuenta en SendGrid

1. Ve a: https://sendgrid.com/
2. Crea una cuenta gratuita
3. Verifica tu correo electrónico

### Paso 2: Crear API Key

1. En SendGrid, ve a: **Settings** → **API Keys**
2. Clic en **Create API Key**
3. Nombre: `TECHO-Chile-Production`
4. Permisos: **Full Access** (o **Mail Send** mínimo)
5. Clic en **Create & View**
6. **COPIA LA API KEY** (solo se muestra una vez!)

### Paso 3: Configurar en Render

En tu servicio de Render, ve a **Environment** y añade estas variables:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=TU_API_KEY_DE_SENDGRID_AQUI
DEFAULT_FROM_EMAIL=noreply@tudominio.cl
```

**Nota:** El `EMAIL_HOST_USER` siempre es literalmente `apikey` (no cambiar).

### Paso 4: Verificar dominio (Opcional pero recomendado)

1. En SendGrid: **Settings** → **Sender Authentication**
2. Sigue las instrucciones para verificar tu dominio
3. Esto mejora la entrega de correos y evita que vayan a spam

---

## 📧 Opción 2: Gmail (Desarrollo/Pequeña escala)

⚠️ **No recomendado para producción** debido a límites estrictos (500 correos/día)

### Configurar Gmail

1. Habilita "Verificación en 2 pasos" en tu cuenta Gmail
2. Ve a: https://myaccount.google.com/apppasswords
3. Genera una "Contraseña de aplicación" para Django
4. Copia la contraseña generada

### Variables de entorno en Render

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion_de_16_caracteres
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

---

## 📧 Opción 3: Mailgun

Otra alternativa gratuita (5,000 correos/mes gratis)

### Configurar Mailgun

1. Crea cuenta en: https://www.mailgun.com/
2. Verifica tu dominio o usa el sandbox de Mailgun
3. Obtén tus credenciales SMTP

### Variables de entorno

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@tu-dominio-mailgun.mailgun.org
EMAIL_HOST_PASSWORD=tu_password_de_mailgun
DEFAULT_FROM_EMAIL=noreply@tu-dominio.cl
```

---

## 🧪 Probar la Configuración

### Opción 1: Desde Render Shell

```bash
python manage.py shell
```

Luego ejecuta:

```python
from django.core.mail import send_mail

send_mail(
    'Prueba de Configuración',
    'Este es un correo de prueba desde TECHO Chile.',
    'noreply@tudominio.cl',
    ['tu-correo@ejemplo.com'],
    fail_silently=False,
)
```

### Opción 2: Usar el sistema de recuperación

1. Ve a: https://tu-app.onrender.com/recuperar-password/
2. Ingresa un correo existente
3. Revisa tu bandeja de entrada
4. Si todo está bien configurado, recibirás el código

---

## 🔒 Seguridad Implementada

### ✅ Cambios de Seguridad Aplicados

1. **NUNCA se muestra el código en pantalla** (ni en desarrollo ni en producción)
2. Los códigos solo se registran en **logs del servidor** (accesible solo para admins)
3. Si falla el envío del correo, se muestra mensaje de error sin revelar el código
4. Tokens expiran en 15 minutos
5. Tokens de un solo uso (no reutilizables)

### Logs en Render

Para ver los logs y encontrar códigos en caso de emergencia:

```bash
# En Render Dashboard → Logs
# Busca líneas como:
# Email no configurado. Código para usuario@ejemplo.com: ABC123
```

---

## 🚀 Recomendación para Producción

**Usa SendGrid** por las siguientes razones:

✅ Gratuito hasta 100 correos/día  
✅ Fácil configuración  
✅ Funciona perfectamente en Render  
✅ Sin límites de "cuenta sospechosa" como Gmail  
✅ Estadísticas de entrega  
✅ Mejor reputación de dominio  

---

## 📝 Checklist de Implementación

- [ ] Crear cuenta en SendGrid
- [ ] Generar API Key
- [ ] Configurar variables de entorno en Render
- [ ] Reiniciar servicio en Render
- [ ] Probar recuperación de contraseña
- [ ] Verificar que el correo llegue
- [ ] Verificar que NO se muestre el código en pantalla
- [ ] (Opcional) Configurar dominio personalizado en SendGrid

---

## 🆘 Troubleshooting

### El correo no llega

1. ✅ Verifica que las variables de entorno estén configuradas
2. ✅ Revisa los logs de Render para ver errores
3. ✅ Verifica que el correo del destinatario sea válido
4. ✅ Revisa la carpeta de SPAM
5. ✅ En SendGrid, ve a Activity para ver el estado de los correos

### Error: SMTP Authentication Failed

- Verifica que el EMAIL_HOST_USER y EMAIL_HOST_PASSWORD sean correctos
- Para SendGrid, EMAIL_HOST_USER debe ser exactamente `apikey`

### Error: Connection Timeout

- Verifica que EMAIL_PORT sea 587
- Verifica que EMAIL_USE_TLS sea True
- Algunos firewalls bloquean puerto 587, prueba puerto 465 con EMAIL_USE_SSL=True

---

## 💡 Contacto

Si tienes problemas, contacta con el equipo de desarrollo de TECHO Chile.

**Sistema actualizado:** 12 de Noviembre 2025  
**Versión:** 2.0 - Seguridad Mejorada

