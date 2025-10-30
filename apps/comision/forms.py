from django import forms
from apps.evaluacion.models import PreguntaModulo, PeriodoEvaluacion


class PreguntaModuloForm(forms.ModelForm):
    class Meta:
        model = PreguntaModulo
        fields = ["pregunta"]
        widgets = {
            "pregunta": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "rows": 3,
                }
            ),
        }
        labels = {
            "pregunta": "",
        }


class PeriodoEvaluacionForm(forms.ModelForm):
    class Meta:
        model = PeriodoEvaluacion
        fields = ["nombre", "descripcion", "fecha_inicio", "fecha_fin"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "placeholder": "Ej: Evaluación Semestre 1-2025",
                }
            ),
            "descripcion": forms.Textarea(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "rows": 3,
                    "placeholder": "Descripción breve del periodo de evaluación",
                }
            ),
            "fecha_inicio": forms.DateInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "type": "date",
                }
            ),
            "fecha_fin": forms.DateInput(
                attrs={
                    "class": "w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent",
                    "type": "date",
                }
            ),
        }
        labels = {
            "nombre": "Nombre del periodo",
            "descripcion": "Descripción",
            "fecha_inicio": "Fecha de inicio",
            "fecha_fin": "Fecha de finalización",
        }
        help_texts = {
            "nombre": "Nombre identificativo del periodo de evaluación",
            "descripcion": "Información adicional sobre el periodo",
            "fecha_inicio": "Fecha en que los estudiantes podrán comenzar a realizar evaluaciones",
            "fecha_fin": "Fecha límite para que los estudiantes realicen evaluaciones",
        }
