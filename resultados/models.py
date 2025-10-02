from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Count

class ResultadoWOD(models.Model):
    CATEGORIA_CHOICES = [
        ('RX', 'RX'),
        ('Intermedio', 'Intermedio'),
        ('Principiante', 'Principiante'),
    ]
    
    UNIDAD_PESO_CHOICES = [
        ('KG', 'Kilogramos (KG)'),
        ('LB', 'Libras (LB)'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resultados_wod')
    fecha_wod = models.DateField(_("Fecha del WOD"), default=timezone.now)
    categoria = models.CharField(_("Categoría"), max_length=12, choices=CATEGORIA_CHOICES)
    tiempo_minutos = models.PositiveIntegerField(_("Minutos"), default=0)
    tiempo_segundos = models.PositiveIntegerField(_("Segundos"), default=0)
    repeticiones = models.PositiveIntegerField(_("Número de Repeticiones"), blank=True, null=True)
    peso_total = models.FloatField(_("Peso Total"), blank=True, null=True)
    unidad_peso = models.CharField(_("Unidad de Peso"), max_length=2, choices=UNIDAD_PESO_CHOICES, default='KG')
    publico = models.BooleanField(_("¿Resultado público?"), default=True, 
                                 help_text=_("Marcar si deseas que otros usuarios vean este resultado"))
    notas = models.TextField(_("Notas"), blank=True, null=True)
    fecha_creacion = models.DateTimeField(_("Fecha de Creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de Actualización"), auto_now=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.fecha_wod} - {self.categoria}"

    class Meta:
        verbose_name = _("Resultado de WOD")
        verbose_name_plural = _("Resultados de WOD")
        ordering = ['-fecha_wod', '-fecha_creacion']

    @property
    def tiempo_formateado(self):
        return f"{self.tiempo_minutos:02d}:{self.tiempo_segundos:02d}"
    
    @property
    def peso_en_libras(self):
        """Convierte el peso a libras si está en kilogramos"""
        if self.peso_total is None:
            return None
        if self.unidad_peso == 'KG':
            return round(self.peso_total * 2.20462, 2)
        return self.peso_total
    
    @property
    def unidad_display(self):
        """Retorna la unidad de peso para display (siempre en libras para vista pública)"""
        return 'LB'
    
    @property
    def peso_para_visualizacion(self):
        """Retorna el peso convertido a libras para visualización pública"""
        return self.peso_en_libras
    
    @property
    def nombre_usuario(self):
        """Retorna el nombre completo o username del usuario"""
        if self.usuario.get_full_name():
            return self.usuario.get_full_name()
        return self.usuario.username
    
    # Agregar Reaccion y comentarios
    @property
    def total_reacciones(self):
        return self.reacciones.count()
    
    @property
    def reacciones_por_tipo(self):
        return self.reacciones.values('tipo').annotate(total=Count('tipo'))
    
    def usuario_ha_reaccionado(self, usuario, tipo=None):
        if tipo:
            return self.reacciones.filter(usuario=usuario, tipo=tipo).exists()
        return self.reacciones.filter(usuario=usuario).exists()
    
    def get_reaccion_usuario(self, usuario):
        """Obtiene la reacción del usuario actual para este resultado"""
        try:
            return self.reacciones.get(usuario=usuario)
        except self.reacciones.model.DoesNotExist:
            return None
        
    def tiene_reaccion_usuario_tipo(self, usuario, tipo_reaccion):
        """Verifica si un usuario tiene una reacción específica en este resultado"""
        if not usuario or usuario.is_anonymous:
            return False
        try:
            reaccion = self.reacciones.get(usuario=usuario)
            return reaccion.tipo == tipo_reaccion
        except Reaccion.DoesNotExist:
            return False

class Reaccion(models.Model):
    TIPO_REACCIONES = [
        ('me_gusta', '👍 Me Gusta'),
        ('me_encanta', '🫶 Me Encanta'),
        ('muy_fuerte', '💪 Muy Fuerte'),
        ('por_poco', '🤏 Por Poco'),
    ]
    
    resultado = models.ForeignKey(ResultadoWOD, on_delete=models.CASCADE, related_name='reacciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_REACCIONES)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['resultado', 'usuario']
        verbose_name = _("Reacción")
        verbose_name_plural = _("Reacciones")
    
    def __str__(self):
        return f"{self.usuario.username} - {self.get_tipo_display()} - {self.resultado}"

class Comentario(models.Model):
    resultado = models.ForeignKey(ResultadoWOD, on_delete=models.CASCADE, related_name='comentarios')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField(_("Texto del comentario"), max_length=500)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
        verbose_name = _("Comentario")
        verbose_name_plural = _("Comentarios")
    
    def __str__(self):
        return f"{self.usuario.username} - {self.resultado}"

    @property
    def texto_corto(self):
        if len(self.texto) > 100:
            return self.texto[:100] + '...'
        return self.texto