from django.db import models

class PlataformaUser(models.Model):
    ROL_CHOICES = [
        ("ADMIN", "Administrador"),
        ("TRABAJADOR", "Trabajador TECHO"),
        ("FAMILIA", "Familia / Beneficiario"),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    rut = models.CharField(max_length=20, blank=True)

    correo = models.EmailField(unique=True)
    password_plana = models.CharField(max_length=128)

    rol = models.CharField(max_length=20, choices=ROL_CHOICES)

    estado = models.CharField(
        max_length=20,
        default="conectado",
        choices=[
            ("conectado", "Conectado"),
            ("ausente", "Ausente"),
            ("ocupado", "Ocupado"),
            ("desconectado", "Desconectado"),
        ],
    )

    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.rol})"



