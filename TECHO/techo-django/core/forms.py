from django import forms
from .models import Proyecto, Vivienda, RegistroPostventa, Evidencia, Constructora, PerfilUsuario

class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ["correo_personal","telefono","avatar"]

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
