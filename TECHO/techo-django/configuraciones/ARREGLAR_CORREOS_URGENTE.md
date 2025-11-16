# 🚨 ARREGLAR CORREOS - No llegan correos

## Problema
Los correos de recuperación de contraseña no llegan porque:
1. **En desarrollo:** Usa `console.EmailBackend` (solo imprime en consola)
2. **En producción:** Falta configurar SendGrid

---

## ✅ SOLUCIÓN INMEDIATA - SendGrid (5 minutos)

### Paso 1: Crear cuenta SendGrid
https://sendgrid.com/

### Paso 2: Generar API Key
1. Settings → API Keys → Create API Key
2. Nombre: "TECHO-Prod"
3. Permisos: Full Access
4. **COPIAR LA KEY** (solo se muestra una vez)

### Paso 3: Configurar en Render
Ve a tu servicio en Render → Environment

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxxxxxxx
DEFAULT_FROM_EMAIL=noreply@techo.cl
```

⚠️ **IMPORTANTE:** `EMAIL_HOST_USER` DEBE ser exactamente `apikey` (no cambiar)

### Paso 4: Guardar y Reiniciar
Render reiniciará automáticamente.

### Paso 5: Probar
1. Ir a recuperar contraseña
2. Ingresar un correo
3. Revisar bandeja de entrada (y SPAM)

---

## 🧪 PROBAR EN LOCAL (Desarrollo)

Para probar en local sin configurar nada:
```python
# Los correos se imprimen en la consola donde corre el servidor
python manage.py runserver
# Busca líneas como:
# Email no configurado. Código para email@example.com: ABC123
```

---

## 📧 ALTERNATIVA: Gmail (NO recomendado para producción)

Solo si no quieres usar SendGrid:

1. Habilitar "Verificación en 2 pasos" en Gmail
2. Ir a: https://myaccount.google.com/apppasswords
3. Generar contraseña de aplicación
4. En Render:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

⚠️ Límite: 500 correos/día

---

## ✅ VERIFICAR QUE FUNCIONA

```bash
# En Render Shell
python manage.py shell

>>> from django.core.mail import send_mail
>>> send_mail(
...     'Test',
...     'Este es un test',
...     'noreply@techo.cl',
...     ['tu-correo@gmail.com'],
...     fail_silently=False
... )
```

Si retorna `1` = **¡FUNCIONÓ!** ✅

---

**RESUMEN:** Configura SendGrid en Render y reinicia. Toma 5 minutos.

