from django.db import models


# Tabla: Privilegio
# Ejemplos de tipoPrivilegio:
# - "ADMIN"   (jefe .ad@techochile.cl)
# - "TECHO"   (trabajador terreno @techochile.cl)
# - "FAMILIA" (familia beneficiaria / cliente)
class Privilegio(models.Model):
    tipoPrivilegio = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.tipoPrivilegio


# Tabla: Proyecto
# Representa el conjunto habitacional / condominio / proyecto DS49 asociado
class Proyecto(models.Model):
    codigoProyecto = models.CharField(max_length=100, unique=True)
    nomProyecto = models.CharField(max_length=255)
    ubicacion = models.CharField(max_length=255)
    fechaInicio = models.DateField(null=True, blank=True)
    fechaEstiTermi = models.DateField(null=True, blank=True)

    def __str__(self):
        # Ej: "Condominio Los Alerces (DS49)"
        return f"{self.nomProyecto} ({self.codigoProyecto})"


# Tabla: Trabajador (personal TECHO)
# Esto corresponde a TRABAJADOR en tu modelo físico
class Trabajador(models.Model):
    rutTrabajador = models.CharField(max_length=12, unique=True)  # "12.345.678-9"
    nombreTrab = models.CharField(max_length=100)
    apellidoTrab = models.CharField(max_length=100)

    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=100, unique=True)

    contrasenna = models.CharField(max_length=128)  # por ahora texto, luego lo hasheamos
    cargo = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)

    # FK a Privilegio (ej: ADMIN / TECHO)
    privilegio = models.ForeignKey(
        Privilegio,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trabajadores"
    )

    # FK a Proyecto
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="trabajadores"
    )

    def __str__(self):
        # Ej: "Juan Pérez (ric.flores@techochile.cl)"
        return f"{self.nombreTrab} {self.apellidoTrab} ({self.correo})"


# Tabla: Cliente (familia beneficiaria)
# Esto corresponde a CLIENTE en tu modelo físico
class Cliente(models.Model):
    rutCliente = models.CharField(max_length=12, unique=True)  # "12.345.678-9"
    nombreCli = models.CharField(max_length=100)
    apellidoCli = models.CharField(max_length=100)

    telefono = models.CharField(max_length=20, blank=True, null=True)
    correo = models.CharField(max_length=100, unique=True)

    contrasenna = models.CharField(max_length=128)  # igual, simple por ahora

    # Más adelante podríamos vincular cada cliente a un proyecto específico
    # o a la unidad (casa/depto). Por ahora lo dejamos suelto.
    def __str__(self):
        # Ej: "María Castillo (maria.castillo@gmail.com)"
        return f"{self.nombreCli} {self.apellidoCli} ({self.correo})"


# Tabla: Registro Posventa
# Equivale a REGISTRO_POSVENTA en tu modelo
# Esto representa una observación / ticket de postventa
class RegistroPosventa(models.Model):
    TIPO_CHOICES = (
        ("FALLA_CONSTRUCTIVA", "Falla constructiva"),
        ("DAÑO_USO", "Daño por uso"),
        ("OTRO", "Otro"),
    )

    tipoCatastro = models.CharField(max_length=200, choices=TIPO_CHOICES)
    observacion = models.TextField()
    imagen = models.TextField(blank=True, null=True)  # aquí puedes guardar ruta/URL de la foto

    # Relación con proyecto (en tu modelo está ligado a PROYECTO)
    proyecto = models.ForeignKey(
        Proyecto,
        on_delete=models.CASCADE,
        related_name="registros_posventa",
        null=True,
        blank=True,
    )

    # Podríamos agregar referencia a cliente/familia más adelante si hace falta

    fechaCreacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Ej: "Falla constructiva - filtración baño"
        return f"{self.tipoCatastro} - {self.observacion[:40]}..."


# Tabla: Estado Inmueble
# Esto en tu modelo tiene folioInmueble, estado, observacion vinculada a una unidad
class EstadoInmueble(models.Model):
    folioInmueble = models.CharField(max_length=100)  # ej: "Casa 14", "Depto 302"
    estado = models.CharField(max_length=200)         # ej: "Pendiente", "En progreso", "Completada"
    observacion = models.TextField(blank=True, null=True)

    # Relación (simplificada por ahora):
    # Lo atamos a un registro de posventa, para saber "esta vivienda tiene este problema"
    registro = models.ForeignKey(
        RegistroPosventa,
        on_delete=models.CASCADE,
        related_name="estados",
        null=True,
        blank=True,
    )

    fechaActualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Ej: "Depto 302 - Pendiente"
        return f"{self.folioInmueble} - {self.estado}"
