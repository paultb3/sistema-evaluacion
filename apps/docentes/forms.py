from django import forms
from apps.usuarios.models import Usuario
from .models import Docente
from django.contrib.auth.hashers import make_password

class RegistroDocenteForm(forms.ModelForm):
    correo = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    departamento = forms.CharField(max_length=100)

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'password']

    def save(self, commit=True):
        usuario = super().save(commit=False)
        usuario.password = make_password(self.cleaned_data['password'])
        if commit:
            usuario.save()
            Docente.objects.create(usuario=usuario, departamento=self.cleaned_data['departamento'])
        return usuario


class LoginDocenteForm(forms.Form):
    correo = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
