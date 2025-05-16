# entrenamientos/admin.py
from django.contrib import admin
from .models import SesionEntrenamiento

@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_publicacion', 'es_activo')
    list_filter = ('es_activo', 'fecha_publicacion')
    search_fields = ('titulo', 'descripcion')
    actions = ['marcar_como_activo', 'marcar_como_inactivo']

    fieldsets = (
        (None, {
            'fields': ('titulo', 'descripcion', 'es_activo')
        }),
        ('Información de Publicación', {
            'fields': ('fecha_publicacion',),
            'classes': ('collapse',), # Opcional, para colapsar esta sección
        }),
    )

    def marcar_como_activo(self, request, queryset):
        # Primero desactiva todos los demás para asegurar solo uno activo
        SesionEntrenamiento.objects.filter(es_activo=True).update(es_activo=False)
        queryset.update(es_activo=True)
    marcar_como_activo.short_description = "Marcar seleccionados como el entrenamiento activo"

    def marcar_como_inactivo(self, request, queryset):
        queryset.update(es_activo=False)
    marcar_como_inactivo.short_description = "Marcar seleccionados como inactivos"