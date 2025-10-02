# entrenamientos/utils.py
from django.utils import timezone
from django.db import transaction
from .models import SesionEntrenamiento
import logging

logger = logging.getLogger(__name__)

def actualizar_entrenamientos_activos():
    """
    Actualiza el estado 'es_activo' de todas las sesiones de entrenamiento.
    Versión optimizada que evita UPDATEs masivos innecesarios.
    """
    now = timezone.now()
    logger.info(f"Ejecutando actualizar_entrenamientos_activos a las {now.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        with transaction.atomic():
            # Encontrar el entrenamiento que debería estar activo
            entrenamiento_a_activar = SesionEntrenamiento.objects.filter(
                fecha_publicacion__lte=now
            ).order_by('-fecha_publicacion').first()

            # Obtener el entrenamiento actualmente activo
            entrenamiento_activo_actual = SesionEntrenamiento.objects.filter(es_activo=True).first()

            # Si no hay cambios necesarios, salir temprano
            if entrenamiento_activo_actual == entrenamiento_a_activar:
                if entrenamiento_a_activar:
                    logger.info(f"Entrenamiento '{entrenamiento_a_activar.titulo}' ya está activo. No se requieren cambios.")
                else:
                    logger.info("No hay entrenamientos activos y ninguno elegible para activar.")
                return

            # Desactivar todos los entrenamientos primero
            SesionEntrenamiento.objects.filter(es_activo=True).update(es_activo=False)
            logger.info("Todos los entrenamientos activos anteriores fueron desactivados.")

            # Activar el nuevo entrenamiento si existe
            if entrenamiento_a_activar:
                entrenamiento_a_activar.es_activo = True
                entrenamiento_a_activar.save(update_fields=['es_activo'])
                logger.info(f"Entrenamiento '{entrenamiento_a_activar.titulo}' (ID: {entrenamiento_a_activar.id}) activado. Fecha: {entrenamiento_a_activar.fecha_publicacion.strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                logger.info("No hay entrenamientos con fecha de publicación cumplida para activar.")

    except Exception as e:
        logger.error(f"Error al actualizar entrenamientos activos: {str(e)}")
        raise