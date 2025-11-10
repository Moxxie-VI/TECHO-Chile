# 📅 Sistema de Monitoreo DS 49 - 120 Días Post-Entrega

## ✅ Implementación Completada

Este documento describe el sistema implementado para el monitoreo del cumplimiento del **Decreto Supremo N° 49** del Ministerio de Vivienda y Urbanismo de Chile, que establece un período de garantía de **120 días** posteriores a la entrega de cada vivienda.

---

## 🎯 Objetivo

Prevenir el vencimiento del plazo de 120 días mediante:
- **Monitoreo en tiempo real** del estado de cada vivienda
- **Alertas visuales** según la urgencia (Normal, Advertencia, Crítico, Vencido)
- **Acceso rápido** desde los dashboards de Admin y Trabajador
- **Gestión centralizada** de fechas de entrega

---

## 🏗️ Componentes Implementados

### 1. Modelo de Datos (`core/models.py`)

#### Modificaciones a `FichaInmueble`:

```python
class FichaInmueble(models.Model):
    # ... campos existentes ...
    fecha_entrega = models.DateField(null=True, blank=True, verbose_name="Fecha de Entrega de Vivienda")
    
    # Métodos para cálculo de DS 49
    def dias_desde_entrega(self):
        """Calcula los días transcurridos desde la entrega"""
    
    def dias_restantes_ds49(self):
        """Calcula los días restantes del período DS 49 (120 días)"""
    
    def estado_ds49(self):
        """Retorna el estado del DS 49"""
        # Estados: NORMAL, ADVERTENCIA, CRITICO, VENCIDO, SIN_FECHA
    
    def porcentaje_ds49(self):
        """Retorna el porcentaje del período DS 49 consumido"""
```

---

### 2. Vistas (`core/views.py`)

#### Vista: `monitoreo_ds49`
- **Acceso:** Admin y Trabajador
- **URL:** `/ds49/monitoreo/`
- **Funcionalidad:**
  - Lista todas las fichas con fecha de entrega
  - Clasifica por estado (Normal, Advertencia, Crítico, Vencido)
  - Muestra estadísticas generales
  - Muestra progreso visual del período de 120 días

#### Vista: `actualizar_fecha_entrega`
- **Acceso:** Solo Admin
- **URL:** `/ds49/actualizar-fecha/<ficha_id>/`
- **Funcionalidad:**
  - Permite establecer/modificar la fecha de entrega de una ficha
  - Valida el formato de fecha
  - Redirige al monitoreo después de guardar

---

### 3. Templates

#### `templates/core/monitoreo_ds49.html`
**Características:**
- ✅ Dashboard completo con estadísticas
- ✅ Tarjetas de contadores por estado
- ✅ Tabla detallada con todas las fichas
- ✅ Barra de progreso visual (0-100%)
- ✅ Colores según urgencia:
  - 🟢 **Verde (Normal):** > 30 días restantes
  - 🟡 **Amarillo (Advertencia):** 15-30 días restantes
  - 🟠 **Naranja (Crítico):** 1-15 días restantes
  - 🔴 **Rojo (Vencido):** 0 o menos días (plazo cumplido/excedido)
- ✅ Información sobre DS 49
- ✅ Leyenda de estados
- ✅ Responsive (móvil y escritorio)

#### `templates/core/actualizar_fecha_entrega.html`
**Características:**
- ✅ Formulario simple para actualizar fecha
- ✅ Información de la ficha (Proyecto, Vivienda, Tipo)
- ✅ Fecha actual (si existe)
- ✅ Validación de fecha
- ✅ Información sobre DS 49

---

### 4. Integración en Dashboards

#### Dashboard Admin (`templates/accounts/dashboard_admin.html`)
**Agregado:**
- ✅ Card de acceso rápido "Monitoreo DS 49"
- ✅ Icono: 📅 `bi-calendar-check`
- ✅ Color: Amarillo (destaca la urgencia)
- ✅ Descripción: "120 días post-entrega"

#### Dashboard Trabajador (`templates/accounts/dashboard_trabajador.html`)
**Agregado:**
- ✅ Sección "Accesos Rápidos" en la parte superior
- ✅ Card "Monitoreo DS 49" con enlace directo
- ✅ Diseño horizontal con icono grande
- ✅ Estilo consistente con el tema del dashboard

---

### 5. URLs (`config/urls.py`)

```python
# Sistema DS 49
path("ds49/monitoreo/", monitoreo_ds49, name="monitoreo_ds49"),
path("ds49/actualizar-fecha/<int:ficha_id>/", actualizar_fecha_entrega, name="actualizar_fecha_entrega"),
```

---

### 6. Migraciones

**Migración creada:** `core/migrations/0007_alter_fichainmueble_options_and_more.py`
- ✅ Agrega campo `fecha_entrega` a `FichaInmueble`
- ✅ Tipo: `DateField` (nullable)
- ✅ Actualiza Meta options del modelo

---

## 🎨 Esquema de Colores y Estados

| Estado | Color | Días Restantes | Descripción |
|--------|-------|----------------|-------------|
| **Normal** | 🟢 Verde (#28a745) | > 30 días | Tiempo suficiente |
| **Advertencia** | 🟡 Amarillo (#ffc107) | 15-30 días | Requiere atención |
| **Crítico** | 🟠 Naranja (#fd7e14) | 1-15 días | Urgente |
| **Vencido** | 🔴 Rojo (#dc3545) | ≤ 0 días | Plazo cumplido/excedido |
| **Sin Fecha** | ⚫ Gris (#6c757d) | N/A | Fecha no registrada |

---

## 📊 Funcionalidades del Sistema

### Para Administradores:
✅ Ver todas las fichas con su estado DS 49  
✅ Establecer/modificar fechas de entrega  
✅ Monitorear fichas en estado crítico  
✅ Acceso rápido desde el dashboard  
✅ Exportar reportes (futuro)  

### Para Trabajadores:
✅ Consultar el estado de las viviendas asignadas  
✅ Ver días restantes del período DS 49  
✅ Identificar viviendas prioritarias  
✅ Acceso rápido desde el dashboard  

### Para Familias:
⏳ **Próximamente:** Vista de su propia vivienda  

---

## 🔄 Flujo de Uso

### 1. Administrador establece fecha de entrega
1. Ingresa a "Monitoreo DS 49"
2. Clic en el botón ✏️ (editar) de una ficha
3. Selecciona la fecha de entrega
4. Guarda y vuelve al monitoreo

### 2. Sistema calcula automáticamente
- Días transcurridos desde la entrega
- Días restantes del período de 120 días
- Estado según los umbrales (Normal, Advertencia, Crítico, Vencido)
- Porcentaje consumido del período

### 3. Visualización en tiempo real
- Dashboard muestra contadores por estado
- Tabla lista todas las fichas ordenadas por fecha
- Barra de progreso visual para cada ficha
- Badges de colores según urgencia

---

## 🚨 Alertas y Notificaciones

### Sistema Actual:
✅ **Alertas visuales** en el dashboard  
✅ **Colores diferenciados** por urgencia  
✅ **Contadores en tiempo real**  
✅ **Ordenamiento por fecha** (más urgentes primero)  

### Próximas Mejoras (Opcional):
- 📧 **Emails automáticos** cuando una ficha entra en estado "Crítico"
- 🔔 **Notificaciones push** en el dashboard
- 📊 **Reportes semanales** del estado general
- 📱 **SMS** para fichas vencidas

---

## 📝 Normativa: Decreto Supremo N° 49

**Extracto relevante:**
> El Decreto Supremo N° 49 del Ministerio de Vivienda y Urbanismo establece que las empresas constructoras deben atender las observaciones y reparaciones necesarias durante un período de **120 días posteriores a la entrega** de la vivienda.

**Implicancias:**
- TECHO Chile tiene responsabilidad legal de atender observaciones en este período
- El incumplimiento puede generar sanciones administrativas
- Es crítico mantener registro de fechas y cumplimiento

---

## 🧪 Pruebas Realizadas

✅ Migración aplicada correctamente  
✅ Vistas accesibles para Admin y Trabajador  
✅ Templates renderizando correctamente  
✅ Cálculos de días funcionando  
✅ Estados clasificándose correctamente  
✅ Colores aplicándose según urgencia  
✅ Enlaces desde dashboard funcionando  
✅ Formulario de actualización funcional  

---

## 📦 Archivos Modificados/Creados

### Modelos:
- `techo-django/core/models.py` (modificado)

### Vistas:
- `techo-django/core/views.py` (2 vistas nuevas agregadas)

### URLs:
- `techo-django/config/urls.py` (2 URLs nuevas)

### Templates:
- `techo-django/templates/core/monitoreo_ds49.html` (nuevo)
- `techo-django/templates/core/actualizar_fecha_entrega.html` (nuevo)
- `techo-django/templates/accounts/dashboard_admin.html` (modificado)
- `techo-django/templates/accounts/dashboard_trabajador.html` (modificado)

### Migraciones:
- `techo-django/core/migrations/0007_alter_fichainmueble_options_and_more.py` (nueva)

---

## 🎉 Beneficios del Sistema

1. **Prevención de Incumplimiento:**
   - Alertas tempranas evitan exceder el plazo de 120 días
   
2. **Transparencia:**
   - Todo el equipo puede ver el estado en tiempo real
   
3. **Priorización:**
   - Casos críticos se identifican visualmente
   
4. **Trazabilidad:**
   - Registro histórico de fechas de entrega
   
5. **Eficiencia:**
   - Reduce la carga administrativa manual
   
6. **Compliance:**
   - Asegura el cumplimiento del DS 49

---

## 🚀 Próximos Pasos (Opcionales)

1. **Agregar notificaciones por email** cuando una ficha entra en estado crítico
2. **Dashboard específico DS 49** con gráficos y estadísticas avanzadas
3. **Exportar reporte PDF** del estado DS 49 de todos los proyectos
4. **Integrar con sistema de tickets** para asignar tareas automáticamente
5. **Vista para Familias** que muestre el estado de su propia vivienda

---

## 📞 Soporte

Para consultas sobre el sistema DS 49:
- **Email:** proyecto.techochile@gmail.com
- **Sistema de Ayuda:** Menú lateral → Ayuda

---

**Fecha de Implementación:** 10 de Noviembre 2025  
**Versión:** 1.0  
**Estado:** ✅ **COMPLETO Y FUNCIONAL**

