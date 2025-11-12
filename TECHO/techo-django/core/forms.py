from django import forms
from .models import Proyecto, Vivienda, RegistroPostventa, Evidencia, Constructora, PerfilUsuario

class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = [
            "rut", "nombre", "apellido", "fecha_nacimiento",
            "correo_personal", "telefono", "telefono_secundario",
            "direccion", "comuna", "region",
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
            'comuna': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Puente Alto, Maipú, etc.'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Metropolitana, Valparaíso, etc.'
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
            'correo_personal': 'Correo Electrónico',
            'telefono': 'Teléfono Principal',
            'telefono_secundario': 'Teléfono Secundario',
            'direccion': 'Dirección',
            'comuna': 'Comuna',
            'region': 'Región',
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
        fields = ["codigo","nombre","ubicacion","constructora","fecha_inicio","fecha_estimada_termino"]
        widgets = {
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ubicacion': forms.TextInput(attrs={'class': 'form-control'}),
            'constructora': forms.Select(attrs={'class': 'form-select'}),
            'fecha_inicio': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'fecha_estimada_termino': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ViviendaForm(forms.ModelForm):
    class Meta:
        model = Vivienda
        fields = ["proyecto","tipo","modelo","cant_cuartos","cant_banos","piso"]

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