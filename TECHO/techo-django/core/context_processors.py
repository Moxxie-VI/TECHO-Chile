from .models import Notificacion

def notificaciones_context(request):
    """
    Context processor para hacer disponibles las notificaciones en todas las plantillas
    """
    if request.user.is_authenticated:
        # Últimas 5 notificaciones para el dropdown del navbar
        notificaciones_recientes = Notificacion.objects.filter(
            usuario=request.user
        ).order_by('-creada_en')[:5]
        
        # Contador de no leídas
        notificaciones_no_leidas_count = Notificacion.objects.filter(
            usuario=request.user,
            leida=False
        ).count()
        
        return {
            'notificaciones_recientes': notificaciones_recientes,
            'notificaciones_no_leidas_count': notificaciones_no_leidas_count,
        }
    
    return {
        'notificaciones_recientes': [],
        'notificaciones_no_leidas_count': 0,
    }
