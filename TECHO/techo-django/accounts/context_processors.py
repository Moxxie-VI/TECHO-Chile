"""
Context processors para agregar variables globales a todos los templates
"""

def user_data(request):
    """
    Agrega información del usuario a todos los templates
    """
    context = {
        'nombre_usuario': 'Usuario',
        'perfil': None,
        'usuario': None,
        'user': None,
    }
    
    try:
        if hasattr(request, 'user') and request.user and request.user.is_authenticated:
            context['usuario'] = request.user
            context['user'] = request.user
            
            # Obtener o crear perfil
            try:
                from core.models import PerfilUsuario
                perfil, _ = PerfilUsuario.objects.get_or_create(user=request.user)
                context['perfil'] = perfil
                
                # Determinar nombre de usuario de forma segura
                if perfil.nombre:
                    context['nombre_usuario'] = perfil.nombre
                elif hasattr(request.user, 'username') and request.user.username:
                    context['nombre_usuario'] = request.user.username
                else:
                    context['nombre_usuario'] = 'Usuario'
                    
            except Exception as e:
                # Si hay algún error con el perfil, intentar con username
                try:
                    if hasattr(request.user, 'username') and request.user.username:
                        context['nombre_usuario'] = request.user.username
                except:
                    context['nombre_usuario'] = 'Usuario'
    except Exception:
        # Si hay cualquier error, usar valores por defecto
        pass
    
    return context

