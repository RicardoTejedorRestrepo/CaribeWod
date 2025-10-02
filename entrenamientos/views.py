# entrenamientos/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from .models import SesionEntrenamiento
from .utils import actualizar_entrenamientos_activos
import logging

logger = logging.getLogger(__name__)

@login_required
def mostrar_entrenamiento_view(request):
    """Vista para mostrar el entrenamiento activo actual"""
    try:
        # Intentar obtener desde cache primero
        cache_key = 'entrenamiento_activo'
        entrenamiento_activo = cache.get(cache_key)
        
        if not entrenamiento_activo:
            # Actualizar estados antes de buscar
            actualizar_entrenamientos_activos()
            
            # Obtener el entrenamiento activo
            entrenamiento_activo = SesionEntrenamiento.objects.filter(
                es_activo=True
            ).select_related().first()
            
            # Cache por 5 minutos
            if entrenamiento_activo:
                cache.set(cache_key, entrenamiento_activo, 300)

        context = {
            'entrenamiento': entrenamiento_activo,
            'page_title': "Plan de Entrenamiento Actual"
        }
        
        return render(request, 'entrenamientos/mostrar_entrenamiento.html', context)
        
    except Exception as e:
        logger.error(f"Error en mostrar_entrenamiento_view: {str(e)}")
        context = {
            'entrenamiento': None,
            'page_title': "Plan de Entrenamiento Actual",
            'error': "Ha ocurrido un error al cargar el entrenamiento."
        }
        return render(request, 'entrenamientos/mostrar_entrenamiento.html', context, status=500)

@login_required
def calculadora_porcentajes(request):
    """Calculadora de porcentajes para entrenamiento"""
    peso_base = None
    incremento = 1
    tabla_porcentajes = []
    error = None
    
    try:
        if request.method == 'POST':
            peso_base_str = request.POST.get('peso_base', '').strip()
            incremento_str = request.POST.get('incremento', '1')
            
            # Validar peso base
            if not peso_base_str:
                error = "Por favor ingresa un peso base."
            else:
                try:
                    peso_base = float(peso_base_str)
                    if peso_base <= 0:
                        error = "El peso base debe ser mayor a 0."
                    elif peso_base > 10000:  # Límite razonable
                        error = "El peso base no puede ser mayor a 10,000."
                    else:
                        incremento = int(incremento_str)
                        if incremento not in [1, 2, 5, 10]:
                            incremento = 1
                        
                        # Calcular tabla de porcentajes
                        for porcentaje in range(0, 101, incremento):
                            if porcentaje == 0:
                                continue  # Saltar 0%
                            valor = peso_base * (porcentaje / 100.0)
                            tabla_porcentajes.append({
                                'porcentaje': porcentaje,
                                'valor': round(valor, 2),
                                'es_entero': valor.is_integer()
                            })
                            
                except ValueError:
                    error = "Por favor ingresa un número válido para el peso base."
                except OverflowError:
                    error = "El peso base es demasiado grande."
    
    except Exception as e:
        logger.error(f"Error en calculadora_porcentajes: {str(e)}")
        error = "Ha ocurrido un error al procesar la calculadora."
    
    context = {
        'peso_base': peso_base,
        'incremento': incremento,
        'tabla_porcentajes': tabla_porcentajes,
        'error': error,
        'page_title': 'Calculadora de Porcentajes'
    }
    return render(request, 'entrenamientos/calculadora_porcentajes.html', context)