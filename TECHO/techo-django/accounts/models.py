from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string

class TokenRecuperacion(models.Model):
    """
    Modelo para almacenar tokens de recuperación de contraseña
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6, unique=True)  # Código de 6 dígitos
    creado_en = models.DateTimeField(auto_now_add=True)
    usado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Token de Recuperación"
        verbose_name_plural = "Tokens de Recuperación"
    
    def __str__(self):
        return f"Token para {self.user.username} - {'Usado' if self.usado else 'Activo'}"
    
    def es_valido(self):
        """
        Verifica si el token aún es válido (no usado y menor a 15 minutos)
        """
        if self.usado:
            return False
        
        tiempo_transcurrido = timezone.now() - self.creado_en
        # El token expira después de 15 minutos
        return tiempo_transcurrido.total_seconds() < 900  # 15 minutos = 900 segundos
    
    @staticmethod
    def generar_codigo():
        """
        Genera un código único de 6 caracteres (números y letras mayúsculas)
        Ejemplo: A3K9M2, B7T4N1, etc.
        """
        caracteres = string.ascii_uppercase + string.digits
        while True:
            codigo = ''.join(secrets.choice(caracteres) for _ in range(6))
            # Verificar que no exista en la base de datos
            if not TokenRecuperacion.objects.filter(token=codigo, usado=False).exists():
                return codigo
