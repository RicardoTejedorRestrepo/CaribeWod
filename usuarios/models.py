# usuarios/models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    nombre_completo = models.CharField(_("Nombre Completo"), max_length=255, blank=True, null=True)
    numero_identificacion = models.CharField(_("Número de Identificación"), max_length=50, blank=True, null=True, unique=True) # Considerar si debe ser único si no es obligatorio
    fecha_nacimiento = models.DateField(_("Fecha de Nacimiento"), blank=True, null=True)
    # RMs (Repetición Máxima)
    rm_snatch = models.FloatField(_("RM Snatch (kg)"), blank=True, null=True)
    rm_clean = models.FloatField(_("RM Clean (kg)"), blank=True, null=True)
    rm_deadlift = models.FloatField(_("RM DeadLift (kg)"), blank=True, null=True)
    rm_front_squat = models.FloatField(_("RM Front Squat (kg)"), blank=True, null=True)
    rm_back_squat = models.FloatField(_("RM Back Squat (kg)"), blank=True, null=True)
    rm_press_banca = models.FloatField(_("RM Press de Banca (kg)"), blank=True, null=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"

# Señal para crear o actualizar el perfil de usuario automáticamente
@receiver(post_save, sender=User)
def crear_o_actualizar_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(user=instance)
    try:
        instance.perfil.save()
    except PerfilUsuario.DoesNotExist: # En caso de que se haya borrado manualmente el perfil y el usuario exista
        PerfilUsuario.objects.create(user=instance)