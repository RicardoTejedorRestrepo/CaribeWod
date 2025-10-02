# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre_completo = models.CharField(_("Nombre Completo"), max_length=255, blank=True, null=True)
    numero_identificacion = models.CharField(_("Número de Identificación"), max_length=50, blank=True, null=True)
    fecha_nacimiento = models.DateField(_("Fecha de Nacimiento"), blank=True, null=True)
    
    # RMs (Repetición Máxima) con validaciones
    rm_snatch = models.FloatField(_("RM Snatch (kg)"), blank=True, null=True, validators=[])
    rm_clean = models.FloatField(_("RM Clean (kg)"), blank=True, null=True, validators=[])
    rm_deadlift = models.FloatField(_("RM DeadLift (kg)"), blank=True, null=True, validators=[])
    rm_front_squat = models.FloatField(_("RM Front Squat (kg)"), blank=True, null=True, validators=[])
    rm_back_squat = models.FloatField(_("RM Back Squat (kg)"), blank=True, null=True, validators=[])
    rm_press_banca = models.FloatField(_("RM Press de Banca (kg)"), blank=True, null=True, validators=[])

    class Meta:
        verbose_name = _('Perfil de Usuario')
        verbose_name_plural = _('Perfiles de Usuario')
        constraints = [
            models.UniqueConstraint(
                fields=['numero_identificacion'],
                condition=models.Q(numero_identificacion__isnull=False),
                name='unique_numero_identificacion_when_not_null'
            )
        ]

    def clean(self):
        """Validaciones adicionales del modelo"""
        if self.fecha_nacimiento and self.fecha_nacimiento.year > 2010:
            raise ValidationError({'fecha_nacimiento': 'Debes ser mayor de 14 años.'})
        
        # Validar que los RMs sean positivos
        rm_fields = ['rm_snatch', 'rm_clean', 'rm_deadlift', 'rm_front_squat', 'rm_back_squat', 'rm_press_banca']
        for field in rm_fields:
            value = getattr(self, field)
            if value and value < 0:
                raise ValidationError({field: 'El valor debe ser positivo.'})

    def __str__(self):
        return f"Perfil de {self.user.username}"

    @property
    def edad(self):
        """Calcula la edad basada en la fecha de nacimiento"""
        if self.fecha_nacimiento:
            from datetime import date
            today = date.today()
            return today.year - self.fecha_nacimiento.year - (
                (today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )
        return None

# Señal optimizada para crear el perfil de usuario
@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    """
    Crea un perfil automáticamente cuando se crea un nuevo usuario.
    """
    if created:
        PerfilUsuario.objects.get_or_create(user=instance)