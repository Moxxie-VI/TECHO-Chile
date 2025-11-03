from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

# --- Ping de prueba ---
@api_view(["GET"])
def ping(request):
    return Response({"message": "API TECHO ok"})

# --- Login JWT ---
@api_view(["POST"])
@permission_classes([AllowAny])
def login_jwt(request):
    email = request.data.get("email")
    password = request.data.get("password")

    # En este sistema usamos el "username" de Django como si fuera correo
    user = authenticate(username=email, password=password)

    if not user:
        return Response({"detail": "Credenciales inválidas"}, status=401)

    # Generar tokens JWT
    refresh = RefreshToken.for_user(user)

    # Lógica de roles:
    # - ADMIN: superuser o staff
    # - TECHO: usuario con dominio techochile.cl pero no superuser
    # - FAMILIA: resto
    role = "FAMILIA"
    if user.is_superuser or user.is_staff:
        role = "ADMIN"
    elif "@techochile.cl" in user.username:
        role = "TECHO"

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        "user_id": user.id,
        "email": user.username,
        "role": role,
    })


# --- Ejemplo de endpoint protegido (para probar después) ---
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def perfil_actual(request):
    """
    Devuelve información básica del usuario autenticado,
    usando el token JWT que el front va a enviar.
    """
    user = request.user
    role = "FAMILIA"
    if user.is_superuser or user.is_staff:
        role = "ADMIN"
    elif "@techochile.cl" in user.username:
        role = "TECHO"

    return Response({
        "id": user.id,
        "email": user.username,
        "role": role,
    })


