from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import Trabajador

def get_user_from_session(request):
    """
    Devuelve dict con info del usuario logeado o None si no hay sesión.
    """
    user_id = request.session.get("user_id")
    user_role = request.session.get("user_role")
    user_email = request.session.get("user_email")

    if user_id and user_role and user_email:
        return {
            "id": user_id,
            "role": user_role,
            "email": user_email,
        }
    return None


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    """
    POST /api/auth/login/
    JSON:
    { "email": "ric.flores.ad@techochile.cl", "password": "techo123" }
    """

    def post(self, request):
        import json
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"detail": "JSON inválido"}, status=400)

        email = data.get("email", "").strip().lower()
        password = data.get("password", "")

        if not email or not password:
            return JsonResponse({"detail": "Faltan credenciales"}, status=400)

        # buscar trabajador por correo
        try:
            trabajador = Trabajador.objects.select_related("privilegio").get(
                correo__iexact=email
            )
        except Trabajador.DoesNotExist:
            return JsonResponse(
                {"detail": "Credenciales inválidas"}, status=401
            )

        # validar contraseña (por ahora texto plano)
        if trabajador.contrasenna != password:
            return JsonResponse(
                {"detail": "Credenciales inválidas"}, status=401
            )

        # sacar rol
        if trabajador.privilegio and trabajador.privilegio.tipoPrivilegio:
            rol = trabajador.privilegio.tipoPrivilegio.upper()
        else:
            rol = "TECHO"

        # guardar sesión django
        request.session["user_id"] = trabajador.id
        request.session["user_role"] = rol            # "ADMIN" o "TECHO"
        request.session["user_email"] = trabajador.correo

        # decidir a dónde lo mandamos
        if rol == "ADMIN":
            destino = "/panel/admin/"
        else:
            destino = "/panel/trabajador/"

        return JsonResponse(
            {
                "detail": "Login ok",
                "redirect": destino,
                "role": rol,
                "email": trabajador.correo,
            },
            status=200,
        )


class MeView(View):
    """
    GET /api/auth/me/
    Esto sirve por si el front quiere saber si ya estás logeado.
    """

    def get(self, request):
        user = get_user_from_session(request)
        if not user:
            return JsonResponse({"isAuthenticated": False}, status=200)
        return JsonResponse({"isAuthenticated": True, "user": user}, status=200)


class LogoutView(View):
    """
    POST /api/auth/logout/
    """

    def post(self, request):
        request.session.flush()
        return JsonResponse({"detail": "Sesión cerrada"}, status=200)


@method_decorator(csrf_exempt, name="dispatch")
class ForgotPasswordView(View):
    """
    POST /api/auth/forgot/
    { "email": "ric.flores.ad@techochile.cl" }

    Demo: confirmamos recepción. No mandamos correo real todavía.
    """

    def post(self, request):
        import json
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"detail": "JSON inválido"}, status=400)

        email = data.get("email", "").strip().lower()
        if not email:
            return JsonResponse(
                {"detail": "Debes indicar tu correo registrado"}, status=400
            )

        # No revelamos si existe o no, por seguridad básica
        return JsonResponse(
            {
                "detail": "Solicitud recibida. Te contactaremos para ayudarte con el acceso."
            },
            status=200,
        )
