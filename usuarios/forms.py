# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Obligatorio. Introduce una dirección de correo válida.")
    # Podrías añadir nombre_completo aquí si quieres pedirlo en el registro inicial
    # nombre_completo = forms.CharField(max_length=255, required=False)


    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

class PerfilUsuarioForm(forms.ModelForm):
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    class Meta:
        model = PerfilUsuario
        fields = [
            'nombre_completo', 'numero_identificacion', 'fecha_nacimiento',
            'rm_snatch', 'rm_clean', 'rm_deadlift', 'rm_front_squat',
            'rm_back_squat', 'rm_press_banca'
        ]
        # widgets = { # Opcional: para mejorar la apariencia de los campos
        #     'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        # }