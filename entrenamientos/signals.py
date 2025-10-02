# entrenamientos/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import SesionEntrenamiento
from .utils import actualizar_entrenamientos_activos
import logging
import threading

logger = logging.getLogger(__name__)

# Usar thread-local storage para evitar problemas en entornos multi-hilo
_thread_local = threading.local()

def get_processing_signal():
    return getattr(_thread_local, 'processing_signal', False)

def set_processing_signal(value):
    _thread_local.processing_signal = value

@receiver(post_save, sender=SesionEntrenamiento)
def al_guardar_o_actualizar_sesion(sender, instance, created, **kwargs):
    """Señal que se ejecuta después de guardar o actualizar una sesión"""
    if get_processing_signal():
        return

    set_processing_signal(True)
    try:
        # Invalidar cache relacionado
        cache_keys = ['entrenamiento_activo', 'entrenamientos_lista']
        for key in cache_keys:
            cache.delete(key)
        
        if created:
            logger.info(f"Nueva sesión creada: '{instance.titulo}' (ID: {instance.id}). Actualizando estados.")
        else:
            logger.info(f"Sesión actualizada: '{instance.titulo}' (ID: {instance.id}). Actualizando estados.")
        
        # Llamar a la lógica para re-evaluar cuál entrenamiento debe estar activo
        actualizar_entrenamientos_activos()
        
    except Exception as e:
        logger.error(f"Error en señal post_save para sesión {instance.id}: {str(e)}")
    finally:
        set_processing_signal(False)

@receiver(post_delete, sender=SesionEntrenamiento)
def al_borrar_sesion(sender, instance, **kwargs):
    """Señal que se ejecuta después de eliminar una sesión"""
    if get_processing_signal():
        return
        
    set_processing_signal(True)
    try:
        # Invalidar cache
        cache.delete('entrenamiento_activo')
        cache.delete('entrenamientos_lista')
        
        logger.info(f"Sesión eliminada: '{instance.titulo}' (ID: {instance.id}). Actualizando estados.")
        
        # Llamar a la lógica para re-evaluar cuál entrenamiento debe estar activo
        actualizar_entrenamientos_activos()
        
    except Exception as e:
        logger.error(f"Error en señal post_delete para sesión {instance.id}: {str(e)}")
    finally:
        set_processing_signal(False)