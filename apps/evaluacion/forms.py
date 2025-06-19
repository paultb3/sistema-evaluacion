from django import forms
from apps.evaluacion.models import Criterio


class CriterioForm(forms.ModelForm):
    class Meta:
        model = Criterio
        fields = ["calificacion"]
        labels = {
            "calificacion": "Calificación",
        }
