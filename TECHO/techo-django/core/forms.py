from django import forms
from .models import Proyecto, Vivienda, RegistroPostventa, Evidencia, Constructora, PerfilUsuario

class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = [
            "rut", "nombre", "apellido", "fecha_nacimiento", "nacionalidad",
            "correo_personal", "telefono", "telefono_secundario",
            "direccion", "ciudad", "comuna", "region",
            "contacto_emergencia_nombre", "contacto_emergencia_telefono", "contacto_emergencia_relacion",
            "avatar", "biografia"
        ]
        widgets = {
            'rut': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '12.345.678-9',
                'maxlength': '12'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Juan Pablo'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: González Pérez'
            }),
            'fecha_nacimiento': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nacionalidad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Chilena, Peruana, Venezolana'
            }),
            'correo_personal': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.cl'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'telefono_secundario': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 8765 4321 (opcional)'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Calle Ejemplo #123, Depto 4'
            }),
            'ciudad': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Santiago, Valparaíso, Concepción'
            }),
            'comuna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Puente Alto, Maipú, etc.'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Metropolitana, Valparaíso, etc.'
            }),
            'contacto_emergencia_nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo de persona de confianza'
            }),
            'contacto_emergencia_telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+56 9 1234 5678'
            }),
            'contacto_emergencia_relacion': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Madre, Hermano, Amigo'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'biografia': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Información adicional sobre ti (opcional)'
            }),
        }
        labels = {
            'rut': 'RUT',
            'nombre': 'Nombre(s)',
            'apellido': 'Apellido(s)',
            'fecha_nacimiento': 'Fecha de Nacimiento',
            'nacionalidad': 'Nacionalidad',
            'correo_personal': 'Correo Electrónico',
            'telefono': 'Teléfono Principal',
            'telefono_secundario': 'Teléfono Secundario',
            'direccion': 'Dirección',
            'ciudad': 'Ciudad',
            'comuna': 'Comuna',
            'region': 'Región',
            'contacto_emergencia_nombre': 'Nombre Persona de Confianza',
            'contacto_emergencia_telefono': 'Teléfono Persona de Confianza',
            'contacto_emergencia_relacion': 'Relación',
            'avatar': 'Foto de Perfil',
            'biografia': 'Sobre mí',
        }

class AyudaForm(forms.Form):
    asunto = forms.CharField(max_length=120, label="Asunto")
    mensaje = forms.CharField(widget=forms.Textarea, label="Mensaje")
    evidencia = forms.FileField(required=False, label="Evidencia (Imagen/PDF opcional)", 
                                help_text="Puedes adjuntar una captura de pantalla o documento PDF")
    
class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = [
            "codigo", "nombre", "constructora",
            "ubicacion", "direccion", "comuna", "region",
            "fecha_inicio", "fecha_estimada_termino", "fecha_entrega_efectiva",
            "encargado_techo", "telefono_encargado",
            "cantidad_viviendas", "descripcion", "estado"
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: PROY-2025-001'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del proyecto'}),
            'constructora': forms.Select(attrs={'class': 'form-select'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ubicación general'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección del proyecto'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Puente Alto'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Metropolitana'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_estimada_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_entrega_efectiva': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'encargado_techo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del encargado'}),
            'telefono_encargado': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+56 9 1234 5678'}),
            'cantidad_viviendas': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del proyecto'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'codigo': 'Código del Proyecto',
            'nombre': 'Nombre',
            'constructora': 'Constructora',
            'ubicacion': 'Ubicación General',
            'direccion': 'Dirección',
            'comuna': 'Comuna',
            'region': 'Región',
            'fecha_inicio': 'Fecha de Inicio',
            'fecha_estimada_termino': 'Fecha Estimada de Término',
            'fecha_entrega_efectiva': 'Fecha de Entrega Efectiva',
            'encargado_techo': 'Encargado TECHO',
            'telefono_encargado': 'Teléfono Encargado',
            'cantidad_viviendas': 'Cantidad de Viviendas',
            'descripcion': 'Descripción',
            'estado': 'Estado del Proyecto',
        }

class ViviendaForm(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = [
            "proyecto", "constructora", "tipo", "modelo", "cant_cuartos", "cant_banos", "piso",
            "direccion", "numero", "block_villa", "comuna", "region", 
            "rut_propietario", "nombre_propietario", "telefono_propietario", "email_propietario"
        ]
        widgets = {
            'proyecto': forms.Select(attrs={'class': 'form-select'}),
            'constructora': forms.Select(attrs={'class': 'form-select'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'modelo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Casa 45m²'}),
            'cant_cuartos': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'cant_banos': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'}),
            'piso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Primer piso, PB'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Calle Los Aromos'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1234 o Depto 4B'}),
            'block_villa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Block A, Villa Los Álamos (opcional)'}),
            'comuna': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Puente Alto'}),
            'region': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Metropolitana'}),
            'rut_propietario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '12.345.678-9', 'id': 'id_rut_propietario'}),
            'nombre_propietario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Juan Pablo Pérez González', 'id': 'id_nombre_propietario'}),
            'telefono_propietario': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: +56 9 1234 5678', 'id': 'id_telefono_propietario'}),
            'email_propietario': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Ej: correo@ejemplo.cl', 'id': 'id_email_propietario'}),
        }
        labels = {
            'proyecto': 'Proyecto',
            'constructora': 'Constructora',
            'tipo': 'Tipo de Vivienda',
            'modelo': 'Modelo',
            'cant_cuartos': 'Cantidad de Cuartos',
            'cant_banos': 'Cantidad de Baños',
            'piso': 'Piso',
            'direccion': 'Dirección (Calle)',
            'numero': 'Número de Casa/Depto',
            'block_villa': 'Block/Villa',
            'comuna': 'Comuna',
            'region': 'Región',
            'rut_propietario': 'RUT Propietario/Beneficiario',
            'nombre_propietario': 'Nombre Completo del Propietario',
            'telefono_propietario': 'Teléfono de Contacto',
            'email_propietario': 'Email del Propietario',
        }

class RegistroPostventaForm(forms.ModelForm):
    class Meta:
        model = RegistroPostventa
        fields = ["proyecto","ficha","recinto","observacion","urgencia","estado"]

class EvidenciaForm(forms.ModelForm):
    class Meta:
        model = Evidencia
        fields = ["archivo","comentario"]

class ConstructoraForm(forms.ModelForm):
    class Meta:
        model = Constructora
        fields = ["rut", "nombre", "direccion", "correo"]
        widgets = {
            'rut': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 12.345.678-9'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la constructora'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección (opcional)'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.cl (opcional)'}),
        }
        labels = {
            'rut': 'RUT',
            'nombre': 'Nombre',
            'direccion': 'Dirección',
            'correo': 'Correo Electrónico',
        }

class ObservacionFamiliaForm(forms.ModelForm):
    """Formulario simplificado para que las familias reporten observaciones"""
    
    CATEGORIAS = (
        ('Puerta Principal', 'Puerta Principal'),
        ('Puerta Interior', 'Puerta Interior'),
        ('Ventana', 'Ventana'),
        ('Baño', 'Baño'),
        ('Cocina', 'Cocina'),
        ('Dormitorio', 'Dormitorio'),
        ('Living/Comedor', 'Living/Comedor'),
        ('Piso', 'Piso'),
        ('Muros/Paredes', 'Muros/Paredes'),
        ('Techo', 'Techo'),
        ('Instalación Eléctrica', 'Instalación Eléctrica'),
        ('Instalación de Agua', 'Instalación de Agua'),
        ('Instalación de Gas', 'Instalación de Gas'),
        ('Otro', 'Otro'),
    )
    
    URGENCIAS = (
        ('BAJA', 'Baja - No es urgente'),
        ('MEDIA', 'Media - Requiere atención pronto'),
        ('ALTA', 'Alta - Requiere atención inmediata'),
    )
    
    recinto = forms.ChoiceField(
        choices=CATEGORIAS,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'id_categoria'
        }),
        label='¿Dónde está el problema?'
    )
    
    observacion = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Describe el problema con el mayor detalle posible. Por ejemplo: "La puerta no cierra bien, tiene un ruido al abrirse"',
            'id': 'id_descripcion'
        }),
        label='Describe el problema',
        help_text='Cuéntanos qué está pasando con el mayor detalle posible'
    )
    
    urgencia = forms.ChoiceField(
        choices=URGENCIAS,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label='Nivel de urgencia',
        initial='MEDIA',
        help_text='¿Qué tan urgente es este problema?'
    )
    
    # Campo para evidencia (se manejará el múltiple en la vista)
    # No usamos el atributo 'multiple' en el widget porque Django no lo soporta directamente
    # En su lugar, lo añadimos manualmente en el template
    
    class Meta:
        model = RegistroPostventa
        fields = ['recinto', 'observacion', 'urgencia']