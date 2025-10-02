# entrenamientos/apps.py
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _
import logging

logger = logging.getLogger(__name__)

class EntrenamientosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'entrenamientos'
    verbose_name = _("Gestión de Entrenamientos")

    def ready(self):
        """Cargar señales cuando la aplicación esté lista"""
        try:
            # Importar señales para que se registren
            from . import signals
            logger.info("Señales de 'entrenamientos' cargadas correctamente.")
        except ImportError as e:
            logger.error(f"Error al importar señales de 'entrenamientos': {e}")