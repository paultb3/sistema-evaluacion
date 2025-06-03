from django import forms


class LoginForm(forms.Form):
    correo = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "email",
                "class": "w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "contraseña",
                "class": "w-full px-4 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500",
            }
        )
    )
