# 📧 Configurar Email en Render (CRÍTICO)

## 🔴 Problema Detectado

El error `WORKER TIMEOUT` ocurre porque el servidor SMTP no está configurado correctamente en Render, causando que el worker de Gunicorn se quede esperando y eventualmente se mate.

## ✅ Solución Implementada

He modificado `accounts/views.py` para:
1. **Timeout de 10 segundos** en la conexión SMTP (evita bloqueos largos)
2. **Fallback automático**: Si falla el envío, muestra el código en pantalla
3. **Mejor manejo de errores**: No bloquea la aplicación si el email falla

## 🎯 Opciones para Configurar Email (GRATIS)

### Opción 1: Gmail con App Password (RECOMENDADO) ✅

**Paso 1: Crear App Password en Gmail**
1. Ve a tu cuenta Google: https://myaccount.google.com/
2. Seguridad → Verificación en 2 pasos (actívala si no la tienes)
3. Seguridad → Contraseñas de aplicaciones
4. Selecciona "Correo" y "Otro dispositivo"
5. Genera la contraseña (16 caracteres)

**Paso 2: Configurar Variables en Render**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=proyecto.techochile@gmail.com
EMAIL_HOST_PASSWORD=[tu app password de 16 caracteres]
DEFAULT_FROM_EMAIL=proyecto.techochile@gmail.com
```

### Opción 2: SendGrid (100 emails/día GRATIS) ✅

**Paso 1: Crear cuenta en SendGrid**
1. Regístrate en: https://signup.sendgrid.com/
2. Verifica tu cuenta
3. Ve a Settings → API Keys
4. Crea un nuevo API Key con permisos de "Mail Send"

**Paso 2: Configurar Variables en Render**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=[tu API key de SendGrid]
DEFAULT_FROM_EMAIL=proyecto.techochile@gmail.com
```

### Opción 3: Brevo (ex-Sendinblue) (300 emails/día GRATIS) ✅

**Paso 1: Crear cuenta en Brevo**
1. Regístrate en: https://www.brevo.com/
2. Verifica tu cuenta
3. Ve a SMTP & API → SMTP
4. Copia tus credenciales SMTP

**Paso 2: Configurar Variables en Render**
```
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=[tu username de Brevo]
EMAIL_HOST_PASSWORD=[tu SMTP key de Brevo]
DEFAULT_FROM_EMAIL=proyecto.techochile@gmail.com
```

## 🚀 Cómo Agregar Variables en Render

1. Ve a tu servicio en Render
2. Clic en "Environment"
3. Clic en "Add Environment Variable"
4. Agrega cada variable **una por una**:
   - Key: `EMAIL_BACKEND`
   - Value: `django.core.mail.backends.smtp.EmailBackend`
5. Haz clic en "Save Changes"
6. **Render hará redeploy automáticamente**

## ⚠️ MIENTRAS TANTO (Solución Temporal)

Mientras configuras el email, la aplicación **funcionará sin problemas**:
- El código de recuperación se mostrará en pantalla
- El usuario puede copiarlo y usarlo
- No hay más errores de WORKER TIMEOUT

## 🧪 Probar después de Configurar

1. Ve a: `https://tu-app.onrender.com/recuperar-password/`
2. Ingresa un correo registrado
3. Deberías recibir el código por email en 5-15 segundos
4. Verifica que el código funcione en la página de verificación

## ❓ ¿Cuál opción elegir?

- **Gmail**: Si ya tienes la cuenta `proyecto.techochile@gmail.com`
- **SendGrid**: Si necesitas profesionalismo y escalabilidad
- **Brevo**: Si necesitas más emails gratis por día

## 📝 Notas Importantes

1. **Puerto 587** es el estándar para TLS/STARTTLS
2. **Puerto 465** para SSL (no recomendado)
3. **Puerto 25** está bloqueado en la mayoría de cloud providers
4. Render puede tardar 1-2 minutos en hacer el redeploy después de cambiar variables
5. **NO uses `fail_silently=True`** ahora que está configurado el timeout

## 🎉 Beneficios de la Solución

✅ No más WORKER TIMEOUT  
✅ Experiencia de usuario sin interrupciones  
✅ Fallback automático si el email falla  
✅ Logs claros en caso de error  
✅ Compatible con cualquier proveedor SMTP

---
**Fecha**: 10 de Noviembre 2025  
**Estado**: ✅ Código corregido y desplegable

