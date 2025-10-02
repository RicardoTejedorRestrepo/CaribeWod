# usuarios/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import PerfilUsuario

class RegistroUsuarioForm(UserCreationForm):
    email = forms.EmailField(
        required=True, 
        help_text="Obligatorio. Introduce una dirección de correo válida.",
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'tu@email.com'})
    )
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu nombre'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Tu apellido'})
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mejorar estilos de todos los campos
        for field_name, field in self.fields.items():
            if field_name not in ['password1', 'password2']:
                field.widget.attrs.update({'class': 'form-input'})
            if field_name == 'username':
                field.widget.attrs.update({'placeholder': 'Nombre de usuario'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Este email ya está registrado.")
        return email

class PerfilUsuarioForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Nombre",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label="Apellido",
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    email = forms.EmailField(
        required=True, 
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={'class': 'form-input'})
    )
    
    fecha_nacimiento = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}),
        required=False,
        label="Fecha de Nacimiento"
    )
    
    # Campos RM con mejoras
    rm_snatch = forms.FloatField(
        required=False, 
        label="RM Snatch (kg)",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '0'})
    )
    rm_clean = forms.FloatField(
        required=False,
        label="RM Clean (kg)", 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '0'})
    )
    rm_deadlift = forms.FloatField(
        required=False,
        label="RM DeadLift (kg)",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '0'})
    )
    rm_front_squat = forms.FloatField(
        required=False,
        label="RM Front Squat (kg)", 
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '0'})
    )
    rm_back_squat = forms.FloatField(
        required=False,
        label="RM Back Squat (kg)",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '0'})
    )
    rm_press_banca = forms.FloatField(
        required=False,
        label="RM Press de Banca (kg)",
        widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.5', 'min': '0'})
    )
    
    class Meta:
        model = PerfilUsuario
        fields = [
            'nombre_completo', 'numero_identificacion', 'fecha_nacimiento',
            'rm_snatch', 'rm_clean', 'rm_deadlift', 'rm_front_squat',
            'rm_back_squat', 'rm_press_banca'
        ]
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'class': 'form-input'}),
            'numero_identificacion': forms.TextInput(attrs={'class': 'form-input'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.instance and self.instance.user:
            if User.objects.filter(email=email).exclude(id=self.instance.user.id).exists():
                raise ValidationError("Este email ya está en uso por otro usuario.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        # Validación adicional para fecha de nacimiento
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento:
            from datetime import date
            today = date.today()
            age = today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            if age < 14:
                raise ValidationError({'fecha_nacimiento': 'Debes tener al menos 14 años.'})
        
        return cleaned_data