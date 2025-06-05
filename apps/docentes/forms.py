from django import forms
from .models import Docente

class PerfilDocenteForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = ['departamento', 'especialidad', 'grado_academico', 'fecha_ingreso']
        widgets = {
            'fecha_ingreso': forms.DateInput(attrs={'type': 'date'}),
        }
