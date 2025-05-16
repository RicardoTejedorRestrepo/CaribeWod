# entrenamientos/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import SesionEntrenamiento

@login_required # Asegura que solo usuarios logueados puedan ver el entrenamiento
def mostrar_entrenamiento_view(request):
    # Obtener el entrenamiento marcado como 'es_activo'
    # Si puede haber más de uno, toma el más reciente
    entrenamiento_activo = SesionEntrenamiento.objects.filter(es_activo=True).order_by('-fecha_publicacion').first()
    context = {
        'entrenamiento': entrenamiento_activo
    }
    return render(request, 'entrenamientos/mostrar_entrenamiento.html', context)