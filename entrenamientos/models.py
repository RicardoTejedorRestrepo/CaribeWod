# entrenamientos/models.py
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class SesionEntrenamiento(models.Model):
    titulo = models.CharField(
        _("Título del Entrenamiento"), 
        max_length=200,
        help_text=_("Título descriptivo del plan de entrenamiento")
    )
    descripcion = models.TextField(
        _("Descripción Detallada"), 
        help_text=_("Puedes usar HTML simple para formatear. Por ejemplo: &lt;strong&gt;texto en negrita&lt;/strong&gt;, &lt;br&gt; para saltos de línea.")
    )
    fecha_publicacion = models.DateTimeField(
        _("Fecha y Hora de Publicación"),
        default=timezone.now,
        help_text=_("El entrenamiento se considerará para activación a partir de esta fecha y hora.")
    )
    es_activo = models.BooleanField(
        _("¿Es el entrenamiento activo actualmente?"),
        default=False,
        help_text=_("Este campo se actualiza automáticamente basado en la fecha de publicación. El más reciente con fecha cumplida será el activo.")
    )
    
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    def clean(self):
        """Validaciones adicionales del modelo"""
        if self.fecha_publicacion and self.fecha_publicacion > timezone.now() + timezone.timedelta(days=365):
            raise ValidationError({
                'fecha_publicacion': _('La fecha de publicación no puede ser más de un año en el futuro.')
            })
        
        if len(self.titulo.strip()) < 3:
            raise ValidationError({
                'titulo': _('El título debe tener al menos 3 caracteres.')
            })

    def __str__(self):
        estado = _("Activo") if self.es_activo else _("Inactivo")
        fecha_formateada = self.fecha_publicacion.strftime('%d/%m/%Y %H:%M')
        return f"{self.titulo} ({fecha_formateada}) - {estado}"

    class Meta:
        verbose_name = _("Sesión de Entrenamiento")
        verbose_name_plural = _("Sesiones de Entrenamiento")
        ordering = ['-fecha_publicacion']
        indexes = [
            models.Index(fields=['es_activo', 'fecha_publicacion']),
            models.Index(fields=['fecha_publicacion']),
        ]