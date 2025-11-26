from django.db import models
from django.contrib.auth.models import User

ESTADOS = (
    ("ABIERTA", "Abierta"),
    ("EN_GESTION", "En gestión"),
    ("RESUELTA", "Resuelta"),
)
class Privilegio(models.Model):
    nombre = models.CharField(max_length=50, unique=True)  # Admin, Trabajador, Familia
    def __str__(self): return self.nombre

class Constructora(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=150)
    direccion = models.CharField(max_length=200, blank=True)
    correo = models.EmailField(blank=True)
    def __str__(self): return self.nombre

class Proyecto(models.Model):
    # IDENTIFICACIÓN
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código Proyecto")
    nombre = models.CharField(max_length=150, verbose_name="Nombre del Proyecto")
    
    # UBICACIÓN
    ubicacion = models.CharField(max_length=200, blank=True, verbose_name="Ubicación")
    comuna = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    region = models.CharField(max_length=100, blank=True, verbose_name="Región")
    direccion = models.CharField(max_length=250, blank=True, verbose_name="Dirección del Proyecto")
    
    # FECHAS
    fecha_inicio = models.DateField(null=True, blank=True, verbose_name="Fecha de Inicio")
    fecha_estimada_termino = models.DateField(null=True, blank=True, verbose_name="Fecha Estimada de Término")
    fecha_entrega_efectiva = models.DateField(null=True, blank=True, verbose_name="Fecha Entrega Efectiva")
    
    # CONSTRUCTORA Y GESTIÓN
    constructora = models.ForeignKey(Constructora, null=True, blank=True, on_delete=models.SET_NULL)
    encargado_techo = models.CharField(max_length=200, blank=True, verbose_name="Encargado TECHO")
    telefono_encargado = models.CharField(max_length=30, blank=True, verbose_name="Teléfono Encargado")
    
    # INFORMACIÓN ADICIONAL
    cantidad_viviendas = models.IntegerField(null=True, blank=True, verbose_name="Cantidad Total de Viviendas")
    descripcion = models.TextField(blank=True, verbose_name="Descripción del Proyecto")
    estado = models.CharField(
        max_length=50,
        choices=(
            ("PLANIFICACION", "Planificación"),
            ("EN_CONSTRUCCION", "En Construcción"),
            ("ENTREGADO", "Entregado"),
            ("POSTVENTA", "En Postventa"),
            ("FINALIZADO", "Finalizado")
        ),
        default="PLANIFICACION",
        verbose_name="Estado del Proyecto"
    )
    
    def __str__(self): return f"{self.codigo} - {self.nombre}"

class Vivienda(models.Model):
    TIPO = (("CASA","CASA"),("DEPARTAMENTO","DEPARTAMENTO"))
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, related_name="viviendas")
    constructora = models.ForeignKey(Constructora, on_delete=models.SET_NULL, null=True, blank=True, 
                                     verbose_name="Constructora", help_text="Constructora asignada a esta vivienda")
    
    # IDENTIFICACIÓN DE LA VIVIENDA
    tipo = models.CharField(max_length=20, choices=TIPO)
    modelo = models.CharField(max_length=100, blank=True)
    cant_cuartos = models.IntegerField(null=True, blank=True, verbose_name="Cantidad de Cuartos")
    cant_banos = models.IntegerField(null=True, blank=True, verbose_name="Cantidad de Baños")
    piso = models.CharField(max_length=50, blank=True, verbose_name="Piso")
    
    # UBICACIÓN DE LA VIVIENDA
    direccion = models.CharField(max_length=250, blank=True, verbose_name="Dirección", help_text="Calle principal")
    numero = models.CharField(max_length=20, blank=True, verbose_name="Número de Casa/Depto")
    block_villa = models.CharField(max_length=50, blank=True, verbose_name="Block/Villa", help_text="Opcional")
    comuna = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    region = models.CharField(max_length=100, blank=True, verbose_name="Región")
    
    # PROPIETARIO/BENEFICIARIO (FAMILIA)
    rut_propietario = models.CharField(
        max_length=12,
        blank=True,
        verbose_name="RUT Propietario",
        help_text="RUT de la familia beneficiaria (ej: 12.345.678-9)"
    )
    nombre_propietario = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Nombre Completo Propietario",
        help_text="Nombre y apellidos del beneficiario"
    )
    telefono_propietario = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Teléfono de Contacto",
        help_text="Teléfono del propietario"
    )
    email_propietario = models.EmailField(
        blank=True,
        verbose_name="Email Propietario",
        help_text="Correo electrónico del beneficiario"
    )
    
    def __str__(self): 
        if self.direccion and self.numero:
            return f"{self.proyecto.codigo} - {self.direccion} #{self.numero}"
        elif self.nombre_propietario:
            return f"{self.proyecto.codigo} - {self.nombre_propietario}"
        return f"{self.proyecto.codigo}-{self.id}-{self.tipo}"
    
    def get_direccion_completa(self):
        """Retorna la dirección completa formateada"""
        parts = [self.direccion, self.numero, self.block_villa, self.comuna, self.region]
        return ", ".join([p for p in parts if p])
    
    class Meta:
        verbose_name = "Vivienda"
        verbose_name_plural = "Viviendas"
        ordering = ['proyecto__codigo', 'numero']

class FichaInmueble(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    vivienda = models.ForeignKey(Vivienda, on_delete=models.CASCADE)
    fecha_entrega = models.DateField(null=True, blank=True, verbose_name="Fecha de Entrega de Vivienda")
    
    class Meta:
        unique_together = ("proyecto","vivienda")
        verbose_name = "Ficha de Inmueble"
        verbose_name_plural = "Fichas de Inmuebles"
    
    def dias_desde_entrega(self):
        """Calcula los días transcurridos desde la entrega"""
        if not self.fecha_entrega:
            return None
        from django.utils import timezone
        delta = timezone.now().date() - self.fecha_entrega
        return delta.days
    
    def dias_restantes_ds49(self):
        """Calcula los días restantes del período DS 49 (120 días)"""
        if not self.fecha_entrega:
            return None
        dias = self.dias_desde_entrega()
        return 120 - dias
    
    def estado_ds49(self):
        """
        Retorna el estado del DS 49 según los días TRANSCURRIDOS desde la entrega.
        
        - NORMAL:      0–30 días
        - ADVERTENCIA: 31–60 días
        - CRITICO:     61–120 días
        - VENCIDO:     >120 días
        """
        dias = self.dias_desde_entrega()
        if dias is None:
            return "SIN_FECHA"
        if dias < 0:
            return "SIN_FECHA"
        if dias <= 30:
            return "NORMAL"
        if dias <= 60:
            return "ADVERTENCIA"
        if dias <= 120:
            return "CRITICO"
        return "VENCIDO"
    
    def porcentaje_ds49(self):
        """Retorna el porcentaje del período DS 49 consumido"""
        if not self.fecha_entrega:
            return 0
        dias = self.dias_desde_entrega()
        if dias < 0:
            return 0
        if dias > 120:
            return 100
        return int((dias / 120) * 100)

class EstadoInmueble(models.Model):
    ESTADOS = (
    ("ABIERTA", "Abierta"),
    ("EN_GESTION", "En gestión"),
    ("RESUELTA", "Resuelta"),
    )
    ficha = models.ForeignKey(FichaInmueble, on_delete=models.CASCADE)
    folio = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS)
    observacion = models.TextField(blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)

class RegistroPostventa(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    ficha = models.ForeignKey(FichaInmueble, on_delete=models.CASCADE)
    reportante = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    recinto = models.CharField(max_length=150)  # baño, cocina, etc.
    observacion = models.TextField()
    urgencia = models.CharField(max_length=20, default="MEDIA")
    vence_en = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="ABIERTA")
    creado_en = models.DateTimeField(auto_now_add=True)

class Evidencia(models.Model):
    registro = models.ForeignKey("RegistroPostventa", on_delete=models.CASCADE, related_name="evidencias")
    archivo = models.FileField(upload_to="evidencias/")
    comentario = models.CharField(max_length=255, blank=True)
    subido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Evidencia {self.id} - {self.registro_id}"


class RegistroComentario(models.Model):
    registro = models.ForeignKey("RegistroPostventa", on_delete=models.CASCADE, related_name="comentarios")
    autor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-creado_en",)

    def __str__(self):
        return f"Comentario {self.id} - Registro {self.registro_id}"

class Reporte(models.Model):
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=200)
    estado = models.CharField(max_length=50, default="GENERADO")
    pdf = models.FileField(upload_to="reportes/", blank=True)  # para descargar
    enviado_a = models.TextField(blank=True)                   # correos separados por coma
    creado_en = models.DateTimeField(auto_now_add=True)

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="perfil")
    rol = models.CharField(max_length=20, choices=(
        ("Admin","Admin"),("Trabajador","Trabajador"),("Familia","Familia")
    ))
    
    # IDENTIFICACIÓN (CRÍTICO PARA CHILE)
    rut = models.CharField(
        max_length=12, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name="RUT",
        help_text="Formato: 12.345.678-9"
    )
    
    # ASIGNACIONES
    proyecto_asignado = models.ForeignKey(Proyecto, null=True, blank=True, on_delete=models.SET_NULL)
    vivienda_asignada = models.ForeignKey(Vivienda, null=True, blank=True, on_delete=models.SET_NULL)
    
    # INFORMACIÓN PERSONAL COMPLETA
    nombre = models.CharField(max_length=100, blank=True, verbose_name="Nombre(s)")
    apellido = models.CharField(max_length=100, blank=True, verbose_name="Apellido(s)")
    fecha_nacimiento = models.DateField(null=True, blank=True, verbose_name="Fecha de Nacimiento")
    nacionalidad = models.CharField(max_length=100, blank=True, default="Chilena", verbose_name="Nacionalidad")
    
    # CONTACTO
    correo_personal = models.EmailField(blank=True, null=True, verbose_name="Correo Personal")
    telefono = models.CharField(max_length=30, blank=True, verbose_name="Teléfono Principal")
    telefono_secundario = models.CharField(max_length=30, blank=True, verbose_name="Teléfono Secundario")
    
    # PERSONA DE CONFIANZA / CONTACTO DE EMERGENCIA
    contacto_emergencia_nombre = models.CharField(max_length=200, blank=True, verbose_name="Nombre Persona de Confianza")
    contacto_emergencia_telefono = models.CharField(max_length=30, blank=True, verbose_name="Teléfono Persona de Confianza")
    contacto_emergencia_relacion = models.CharField(max_length=100, blank=True, verbose_name="Relación", help_text="Ej: Madre, Hermano, Amigo")
    
    # DIRECCIÓN
    direccion = models.CharField(max_length=250, blank=True, verbose_name="Dirección")
    ciudad = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    comuna = models.CharField(max_length=100, blank=True, verbose_name="Comuna")
    region = models.CharField(max_length=100, blank=True, verbose_name="Región")
    
    # OTROS
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True, verbose_name="Foto de Perfil")
    biografia = models.TextField(blank=True, verbose_name="Biografía", help_text="Información adicional")
    
    # METADATA
    actualizado_en = models.DateTimeField(auto_now=True, verbose_name="Última Actualización")

    def __str__(self):
        return f"{self.user.username} ({self.rol})"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del usuario"""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        elif self.nombre:
            return self.nombre
        elif self.apellido:
            return self.apellido
        return self.user.username
    
    def get_rut_formateado(self):
        """Retorna el RUT formateado con puntos y guión"""
        if not self.rut:
            return "Sin RUT"
        # Remover caracteres no numéricos excepto el dígito verificador
        rut = self.rut.replace(".", "").replace("-", "")
        if len(rut) < 2:
            return self.rut
        # Separar cuerpo y dígito verificador
        cuerpo = rut[:-1]
        dv = rut[-1]
        # Formatear con puntos
        cuerpo_formateado = "{:,}".format(int(cuerpo)).replace(",", ".")
        return f"{cuerpo_formateado}-{dv}"
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"