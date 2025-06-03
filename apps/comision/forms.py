from django import forms
from apps.evaluacion.models import PreguntaModulo


class PreguntaModuloForm(forms.ModelForm):
    class Meta:
        model = PreguntaModulo
        fields = ["pregunta"]
        widgets = {
            "pregunta": forms.Textarea(attrs={"rows": 4, "cols": 50}),
        }
