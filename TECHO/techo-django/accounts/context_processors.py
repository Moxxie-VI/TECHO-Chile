"""
Context processors para agregar variables globales a todos los templates
"""

def user_data(request):
    """
    Agrega información del usuario a todos los templates
    """
    context = {
        'nombre_usuario': None,
        'perfil': None,
        'usuario': None,
    }
    
    if request.user.is_authenticated:
        context['usuario'] = request.user
        
        # Obtener o crear perfil
        try:
            from .models import PerfilUsuario
            perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
            context['perfil'] = perfil
            context['nombre_usuario'] = perfil.nombre or request.user.username
        except Exception:
            # Si hay algún error, usar username
            context['nombre_usuario'] = request.user.username
    
    return context

