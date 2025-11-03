from django.http import HttpResponseForbidden
from functools import wraps

def require_role(*roles):
    def inner(view):
        @wraps(view)
        def wrapper(request, *args, **kwargs):
            perfil = getattr(request.user, "perfil", None)
            user_role = (perfil.rol if perfil else None) or ("Admin" if request.user.is_superuser else None)
            if user_role in roles:
                return view(request, *args, **kwargs)
            return HttpResponseForbidden("No tienes permisos suficientes.")
        return wrapper
    return inner
