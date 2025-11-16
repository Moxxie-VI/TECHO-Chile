# 🚀 Cómo Desplegar los Cambios en Render

## 📋 Resumen

Has realizado **cambios importantes** en el código:
- ✅ 3 dashboards rediseñados
- ✅ Nueva funcionalidad de Fichas de Inmuebles
- ✅ Navbar mejorado
- ✅ Fix del error de login

## 🔄 Opciones para Desplegar en Render

### Opción 1: Push a Git (Recomendado)

Render está configurado para hacer **deploy automático** cuando haces push a tu repositorio de GitHub.

**Pasos:**

```bash
# 1. Verificar cambios
git status

# 2. Agregar todos los archivos modificados
git add .

# 3. Hacer commit con mensaje descriptivo
git commit -m "feat: Rediseño completo de dashboards y nueva funcionalidad de Fichas de Inmuebles"

# 4. Push a GitHub (rama main o master)
git push origin main
```

**Resultado:**
- Render detectará el push automáticamente
- Iniciará el build y deploy
- En 2-5 minutos los cambios estarán en producción

---

### Opción 2: Deploy Manual desde Render Dashboard

Si prefieres más control:

1. **Ve a tu dashboard de Render:** https://dashboard.render.com
2. **Selecciona tu servicio:** `techo-chile`
3. **Click en "Manual Deploy"**
4. **Selecciona la rama:** `main` o `master`
5. **Click en "Deploy"**

---

## 📦 Archivos que se Desplegarán

### Modificados:
```
✅ templates/accounts/dashboard_admin.html
✅ templates/accounts/dashboard_trabajador.html
✅ templates/accounts/dashboard_familia.html
✅ templates/layout/base.html
✅ accounts/views.py
✅ core/views.py
```

### Nuevos:
```
✅ templates/core/fichas_inmuebles.html
✅ templates/core/detalle_ficha_inmueble.html
```

### Documentación (opcional):
```
📄 CAMBIOS_REALIZADOS_COMPLETO.md
📄 RESUMEN_PARA_USUARIO.md
📄 FIX_ERROR_DASHBOARD.md
📄 DESPLEGAR_EN_RENDER.md (este archivo)
```

---

## ⚙️ Verificación Post-Deploy

Una vez que Render complete el deploy:

### 1. Verificar que el sitio está up:
```
https://techo-chile.onrender.com
```

### 2. Probar funcionalidades clave:

#### ✅ Login:
- [ ] Login como Admin funciona
- [ ] Login como Trabajador funciona
- [ ] Login como Familia funciona

#### ✅ Dashboards:
- [ ] Dashboard Admin se ve correctamente
- [ ] Dashboard Trabajador se ve correctamente
- [ ] Dashboard Familia se ve correctamente

#### ✅ Nueva Funcionalidad:
- [ ] "Fichas de Inmuebles" aparece en navbar
- [ ] Búsqueda por RUT funciona
- [ ] Filtro por proyecto funciona
- [ ] Vista detallada de ficha funciona

#### ✅ Navbar:
- [ ] Enlaces reorganizados correctamente
- [ ] Badges "NUEVO" visibles
- [ ] Dropdowns funcionan

---

## 🐛 Si Algo Sale Mal

### Error 1: "Application Error" en Render

**Causa:** Build falló o hay errores en el código.

**Solución:**
1. Ve a Render Dashboard → Logs
2. Revisa los logs de build y deploy
3. Busca líneas rojas con errores
4. Corrige el error y haz otro push

### Error 2: Estilos no se cargan

**Causa:** Archivos estáticos no se recolectaron.

**Solución:**
```bash
# En tu local, asegúrate de tener:
python manage.py collectstatic --noinput
```

Render debería hacer esto automáticamente con el `build.sh` script.

### Error 3: Cambios no se ven

**Causa:** Caché del navegador.

**Solución:**
1. **Ctrl + Shift + R** (Windows/Linux)
2. **Cmd + Shift + R** (Mac)
3. O abre en ventana privada/incógnito

---

## 📊 Monitoreo

### Logs en Tiempo Real:

```bash
# En Render Dashboard:
Shell → Connect

# Ver logs:
tail -f /var/log/gunicorn.log
```

### Verificar Variables de Entorno:

En Render Dashboard → Environment:
```
✅ DATABASE_URL
✅ SECRET_KEY
✅ DJANGO_SETTINGS_MODULE
✅ EMAIL_* (si usas email)
```

---

## 🔄 Rollback (Si es necesario)

Si algo sale muy mal y necesitas volver atrás:

### Opción A: Rollback en Render
1. Render Dashboard → Service → Deploys
2. Encuentra el deploy anterior que funcionaba
3. Click en "..." → "Redeploy"

### Opción B: Rollback en Git
```bash
# Ver commits anteriores
git log --oneline

# Revertir al commit anterior
git revert HEAD

# O volver a un commit específico
git reset --hard <commit-hash>
git push origin main --force
```

**⚠️ Nota:** `--force` sobrescribe el historial. Úsalo con cuidado.

---

## ✅ Checklist Pre-Deploy

Antes de hacer push, verifica:

- [ ] ✅ Servidor local funciona sin errores
- [ ] ✅ Login funciona para todos los roles
- [ ] ✅ Dashboards se ven correctamente
- [ ] ✅ No hay errores en la consola del navegador (F12)
- [ ] ✅ No hay errores de linting
- [ ] ✅ Migraciones aplicadas (si las hay)
- [ ] ✅ Archivos innecesarios excluidos (.pyc, __pycache__, etc.)

---

## 🎯 Comando Completo para Deploy

```bash
# Todo en uno (desde la raíz del proyecto):

# 1. Verificar estado
git status

# 2. Agregar cambios
git add .

# 3. Commit
git commit -m "feat: Rediseño completo - Dashboards profesionales, Fichas de Inmuebles, Fix login error"

# 4. Push (deploy automático)
git push origin main

# 5. Verificar en Render Dashboard
# https://dashboard.render.com
```

---

## 📞 Soporte

Si tienes problemas durante el deploy:

1. **Revisa los logs de Render**
2. **Verifica que las migraciones se aplicaron**
3. **Confirma que las variables de entorno están configuradas**
4. **Prueba en modo incógnito para evitar caché**

---

## 🎊 Después del Deploy Exitoso

Una vez que todo esté funcionando:

1. ✅ Prueba todos los flujos de usuario
2. ✅ Verifica en diferentes dispositivos (móvil, tablet, desktop)
3. ✅ Comparte el link con tu equipo
4. ✅ ¡Celebra! 🎉

---

**Última actualización:** 12 de Noviembre, 2025  
**Status:** ✅ Listo para Deploy

