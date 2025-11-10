from django import forms
from .models import Proyecto, Vivienda, RegistroPostventa, Evidencia
from django import forms
from .models import PerfilUsuario

class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ["correo_personal","telefono","avatar"]

class AyudaForm(forms.Form):
    asunto = forms.CharField(max_length=120)
    mensaje = forms.CharField(widget=forms.Textarea)
    
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
