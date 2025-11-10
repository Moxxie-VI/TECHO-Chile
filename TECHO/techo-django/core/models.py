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
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    ubicacion = models.CharField(max_length=200, blank=True)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_estimada_termino = models.DateField(null=True, blank=True)
    constructora = models.ForeignKey(Constructora, null=True, blank=True, on_delete=models.SET_NULL)
    def __str__(self): return f"{self.codigo} - {self.nombre}"

class Vivienda(models.Model):
    TIPO = (("CASA","CASA"),("DEPARTAMENTO","DEPARTAMENTO"))
    proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO)
    modelo = models.CharField(max_length=100, blank=True)
    cant_cuartos = models.IntegerField(null=True, blank=True)
    cant_banos = models.IntegerField(null=True, blank=True)
    piso = models.CharField(max_length=50, blank=True)
    def __str__(self): return f"{self.proyecto.codigo}-{self.id}-{self.tipo}"

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
        """Retorna el estado del DS 49"""
        dias_restantes = self.dias_restantes_ds49()
        if dias_restantes is None:
            return "SIN_FECHA"
        elif dias_restantes > 30:
            return "NORMAL"  # Verde
        elif dias_restantes > 15:
            return "ADVERTENCIA"  # Amarillo
        elif dias_restantes > 0:
            return "CRITICO"  # Rojo
        else:
            return "VENCIDO"  # Rojo oscuro
    
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
    proyecto_asignado = models.ForeignKey(Proyecto, null=True, blank=True, on_delete=models.SET_NULL)
    vivienda_asignada = models.ForeignKey(Vivienda, null=True, blank=True, on_delete=models.SET_NULL)
    # Información personal:
    nombre = models.CharField(max_length=100, blank=True)
    apellido = models.CharField(max_length=100, blank=True)
    correo_personal = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=30, blank=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.rol})"