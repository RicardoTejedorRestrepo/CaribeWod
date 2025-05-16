# entrenamientos/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class SesionEntrenamiento(models.Model):
    titulo = models.CharField(_("Título del Entrenamiento"), max_length=200)
    descripcion = models.TextField(_("Descripción Detallada"), help_text=_("Puedes usar HTML simple para formatear."))
    fecha_publicacion = models.DateTimeField(_("Fecha de Publicación"), default=timezone.now)
    # Campo para controlar si este es el entrenamiento "activo" o "del día"
    es_activo = models.BooleanField(
        _("Es el entrenamiento activo"),
        default=True,
        help_text=_("Marca esta casilla si este es el entrenamiento que se debe mostrar actualmente a los usuarios.")
    )

    def __str__(self):
        return f"{self.titulo} ({self.fecha_publicacion.strftime('%d/%m/%Y')})"

    class Meta:
        verbose_name = _("Sesión de Entrenamiento")
        verbose_name_plural = _("Sesiones de Entrenamiento")
        ordering = ['-fecha_publicacion'] # Los más recientes primero

    def save(self, *args, **kwargs):
        # Si este entrenamiento se marca como activo, desactiva los demás
        if self.es_activo:
            SesionEntrenamiento.objects.filter(es_activo=True).exclude(pk=self.pk).update(es_activo=False)
        super().save(*args, **kwargs)