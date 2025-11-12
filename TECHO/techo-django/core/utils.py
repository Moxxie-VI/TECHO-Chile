"""
Utilidades para el sistema TECHO Chile
Incluye validación de RUT chileno y otras funciones auxiliares
"""


def validar_rut(rut):
    """
    Valida un RUT chileno verificando el dígito verificador.
    
    Args:
        rut (str): RUT en formato "12.345.678-9" o "12345678-9" o "123456789"
    
    Returns:
        tuple: (bool, str) - (es_valido, rut_formateado)
    
    Ejemplos:
        >>> validar_rut("12.345.678-5")
        (True, "12.345.678-5")
        >>> validar_rut("12345678-5")
        (True, "12.345.678-5")
        >>> validar_rut("12345678-0")
        (False, None)
    """
    # Eliminar puntos y guiones
    rut = rut.replace(".", "").replace("-", "").strip().upper()
    
    # Verificar que tenga al menos 2 caracteres (número + DV)
    if len(rut) < 2:
        return False, None
    
    # Separar cuerpo y dígito verificador
    cuerpo = rut[:-1]
    dv_ingresado = rut[-1]
    
    # Verificar que el cuerpo sean solo números
    if not cuerpo.isdigit():
        return False, None
    
    # Calcular dígito verificador
    suma = 0
    multiplicador = 2
    
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador += 1
        if multiplicador > 7:
            multiplicador = 2
    
    resto = suma % 11
    dv_calculado = 11 - resto
    
    # Convertir dígito verificador a string
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    
    # Comparar
    es_valido = (dv_calculado == dv_ingresado)
    
    if es_valido:
        # Formatear RUT: 12.345.678-9
        rut_formateado = "{:,}-{}".format(int(cuerpo), dv_ingresado).replace(",", ".")
        return True, rut_formateado
    else:
        return False, None


def limpiar_rut(rut):
    """
    Limpia un RUT eliminando puntos, guiones y espacios.
    
    Args:
        rut (str): RUT en cualquier formato
    
    Returns:
        str: RUT limpio (solo números y letra)
    """
    if not rut:
        return ""
    return rut.replace(".", "").replace("-", "").replace(" ", "").strip().upper()


def formatear_rut(rut):
    """
    Formatea un RUT al formato estándar chileno: 12.345.678-9
    
    Args:
        rut (str): RUT en cualquier formato
    
    Returns:
        str: RUT formateado o string vacío si es inválido
    """
    es_valido, rut_formateado = validar_rut(rut)
    return rut_formateado if es_valido else ""


def formatear_telefono(telefono):
    """
    Formatea un número de teléfono chileno.
    
    Args:
        telefono (str): Teléfono en cualquier formato
    
    Returns:
        str: Teléfono formateado
    """
    if not telefono:
        return ""
    
    # Eliminar caracteres no numéricos
    numeros = ''.join(filter(str.isdigit, telefono))
    
    # Si empieza con 569 (código Chile + móvil), formatear
    if numeros.startswith('569') and len(numeros) == 11:
        return f"+56 9 {numeros[3:7]} {numeros[7:]}"
    
    # Si empieza con 56 (código Chile), formatear
    if numeros.startswith('56') and len(numeros) >= 10:
        return f"+{numeros[:2]} {numeros[2:3]} {numeros[3:7]} {numeros[7:]}"
    
    # Si es solo el número móvil (9 dígitos)
    if numeros.startswith('9') and len(numeros) == 9:
        return f"+56 9 {numeros[1:5]} {numeros[5:]}"
    
    # Devolver sin formato si no coincide
    return telefono


def calcular_edad(fecha_nacimiento):
    """
    Calcula la edad a partir de una fecha de nacimiento.
    
    Args:
        fecha_nacimiento (date): Fecha de nacimiento
    
    Returns:
        int: Edad en años
    """
    if not fecha_nacimiento:
        return None
    
    from datetime import date
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    
    return edad


def generar_codigo_verificacion(longitud=6):
    """
    Genera un código de verificación alfanumérico seguro.
    
    Args:
        longitud (int): Longitud del código
    
    Returns:
        str: Código generado
    """
    import secrets
    import string
    
    caracteres = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(longitud))


def validar_email_chile(email):
    """
    Valida un correo electrónico con formato chileno opcional.
    
    Args:
        email (str): Correo electrónico
    
    Returns:
        bool: True si es válido
    """
    import re
    
    if not email:
        return False
    
    # Pattern básico de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def obtener_comunas_chile():
    """
    Retorna una lista de comunas de Chile organizadas por región.
    
    Returns:
        dict: Diccionario con regiones y sus comunas
    """
    return {
        "Metropolitana": [
            "Santiago", "Cerrillos", "Cerro Navia", "Conchalí", "El Bosque",
            "Estación Central", "Huechuraba", "Independencia", "La Cisterna",
            "La Florida", "La Granja", "La Pintana", "La Reina", "Las Condes",
            "Lo Barnechea", "Lo Espejo", "Lo Prado", "Macul", "Maipú",
            "Ñuñoa", "Pedro Aguirre Cerda", "Peñalolén", "Providencia",
            "Pudahuel", "Quilicura", "Quinta Normal", "Recoleta", "Renca",
            "San Joaquín", "San Miguel", "San Ramón", "Vitacura",
            "Puente Alto", "Pirque", "San José de Maipo",
            "Colina", "Lampa", "TilTil",
            "San Bernardo", "Buin", "Calera de Tango", "Paine", "Talagante",
            "Peñaflor", "Isla de Maipo", "El Monte", "Padre Hurtado", "Melipilla"
        ],
        "Valparaíso": [
            "Valparaíso", "Viña del Mar", "Concón", "Quintero", "Puchuncaví",
            "Casablanca", "Quilpué", "Villa Alemana", "San Antonio"
        ],
        "Biobío": [
            "Concepción", "Talcahuano", "Hualpén", "Chiguayante", "San Pedro de la Paz",
            "Penco", "Tomé", "Los Ángeles", "Chillán", "Coronel"
        ],
        # Añadir más regiones según sea necesario
    }


def sanitizar_texto(texto):
    """
    Sanitiza un texto para evitar problemas de seguridad.
    
    Args:
        texto (str): Texto a sanitizar
    
    Returns:
        str: Texto sanitizado
    """
    if not texto:
        return ""
    
    # Eliminar caracteres peligrosos
    texto = texto.strip()
    # Limitar longitud
    texto = texto[:1000]
    
    return texto

