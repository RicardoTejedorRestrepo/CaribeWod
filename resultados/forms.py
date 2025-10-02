from django import forms
from .models import ResultadoWOD
from .models import Comentario

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Escribe tu comentario...',
                'maxlength': '500'
            })
        }
        labels = {
            'texto': ''
        }

class ResultadoWODForm(forms.ModelForm):
    # Campos adicionales para el tiempo
    tiempo_minutos = forms.IntegerField(
        min_value=0, 
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Min',
            'min': '0'
        })
    )
    
    tiempo_segundos = forms.IntegerField(
        min_value=0, 
        max_value=59,
        initial=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Seg',
            'min': '0',
            'max': '59'
        })
    )
    
    # Hacer el campo público más descriptivo
    publico = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'id_publico_checkbox'
        }),
        help_text="Marcar si deseas que otros usuarios vean este resultado"
    )
    
    class Meta:
        model = ResultadoWOD
        fields = ['fecha_wod', 'categoria', 'tiempo_minutos', 'tiempo_segundos', 
                 'repeticiones', 'peso_total', 'unidad_peso', 'publico', 'notas']
        widgets = {
            'fecha_wod': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'required': 'required'
            }),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'repeticiones': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'placeholder': 'Número de repeticiones'
            }),
            'peso_total': forms.NumberInput(attrs={
                'class': 'form-control', 
                'min': 0, 
                'step': 0.1, 
                'placeholder': 'Peso total'
            }),
            'unidad_peso': forms.Select(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Notas adicionales...'
            }),
        }
        labels = {
            'fecha_wod': 'Fecha del WOD',
            'categoria': 'Categoría',
            'repeticiones': 'Número de Repeticiones',
            'peso_total': 'Peso Total',
            'unidad_peso': 'Unidad de Peso',
            'publico': '¿Hacer público este resultado?',
            'notas': 'Notas',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Asegurar que la fecha se mantenga al editar
        if self.instance and self.instance.pk and self.instance.fecha_wod:
            # Formatear la fecha para el input type="date" (YYYY-MM-DD)
            self.fields['fecha_wod'].initial = self.instance.fecha_wod.strftime('%Y-%m-%d')
            
            # Establecer los valores de tiempo si existen
            if hasattr(self.instance, 'tiempo_minutos'):
                self.fields['tiempo_minutos'].initial = self.instance.tiempo_minutos
            if hasattr(self.instance, 'tiempo_segundos'):
                self.fields['tiempo_segundos'].initial = self.instance.tiempo_segundos

    def clean_tiempo_segundos(self):
        segundos = self.cleaned_data.get('tiempo_segundos')
        if segundos is not None and segundos >= 60:
            raise forms.ValidationError("Los segundos no pueden ser 60 o más.")
        return segundos

    def clean(self):
        cleaned_data = super().clean()
        tiempo_minutos = cleaned_data.get('tiempo_minutos')
        tiempo_segundos = cleaned_data.get('tiempo_segundos')
        repeticiones = cleaned_data.get('repeticiones')
        
        if (not tiempo_minutos or tiempo_minutos == 0) and (not tiempo_segundos or tiempo_segundos == 0) and not repeticiones:
            raise forms.ValidationError(
                "Debes ingresar al menos el tiempo o el número de repeticiones."
            )
        
        return cleaned_data