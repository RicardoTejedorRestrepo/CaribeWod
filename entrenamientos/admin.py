# entrenamientos/admin.py
from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html
from .models import SesionEntrenamiento
from .utils import actualizar_entrenamientos_activos

@admin.register(SesionEntrenamiento)
class SesionEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_publicacion', 'estado_coloreado', 'id', 'acciones_rapidas')
    list_filter = ('es_activo', 'fecha_publicacion')
    search_fields = ('titulo', 'descripcion')
    date_hierarchy = 'fecha_publicacion'
    list_per_page = 20
    
    readonly_fields = ('es_activo', 'fecha_creacion', 'fecha_actualizacion')
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'fecha_publicacion'),
            'description': 'Información principal del entrenamiento'
        }),
        ('Estado Automático', {
            'fields': ('es_activo',),
            'classes': ('collapse',),
            'description': 'Este campo se gestiona automáticamente según la fecha de publicación'
        }),
    )
    
    actions = ['forzar_actualizacion_de_estados_activos_action', 'activar_seleccionados', 'desactivar_seleccionados']

    def estado_coloreado(self, obj):
        """Muestra el estado con colores"""
        if obj.es_activo:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ ACTIVO</span>'
            )
        return format_html(
            '<span style="color: red;">Inactivo</span>'
        )
    estado_coloreado.short_description = 'Estado'
    estado_coloreado.admin_order_field = 'es_activo'

    def acciones_rapidas(self, obj):
        """Botones de acción rápida en la lista"""
        return format_html(
            '''
            <div style="display: flex; gap: 5px;">
                <a href="{}" class="button" style="padding: 2px 8px; background: #417690; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">Editar</a>
                <a href="{}" class="button" style="padding: 2px 8px; background: #ba2121; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">Eliminar</a>
            </div>
            ''',
            f'{obj.id}/change/',
            f'{obj.id}/delete/'
        )
    acciones_rapidas.short_description = 'Acciones'

    def forzar_actualizacion_de_estados_activos_action(self, request, queryset):
        """Acción para forzar la actualización de estados activos"""
        try:
            actualizar_entrenamientos_activos()
            self.message_user(
                request, 
                "✅ Se ha forzado la actualización de los estados activos de los entrenamientos.", 
                messages.SUCCESS
            )
        except Exception as e:
            self.message_user(
                request, 
                f"❌ Error al actualizar estados: {str(e)}", 
                messages.ERROR
            )
    forzar_actualizacion_de_estados_activos_action.short_description = "Forzar actualización de estados activos"

    def activar_seleccionados(self, request, queryset):
        """Activar entrenamientos seleccionados (para testing)"""
        # Primero desactivar todos
        SesionEntrenamiento.objects.update(es_activo=False)
        # Luego activar los seleccionados
        updated = queryset.update(es_activo=True)
        self.message_user(
            request, 
            f"✅ {updated} entrenamientos activados manualmente.", 
            messages.SUCCESS
        )
    activar_seleccionados.short_description = "Activar seleccionados (manual)"

    def desactivar_seleccionados(self, request, queryset):
        """Desactivar entrenamientos seleccionados"""
        updated = queryset.update(es_activo=False)
        self.message_user(
            request, 
            f"✅ {updated} entrenamientos desactivados.", 
            messages.SUCCESS
        )
        
        # Si se desactivó el entrenamiento activo, buscar uno nuevo
        entrenamiento_activo = SesionEntrenamiento.objects.filter(es_activo=True).first()
        if not entrenamiento_activo:
            actualizar_entrenamientos_activos()
    desactivar_seleccionados.short_description = "Desactivar seleccionados"

    def get_readonly_fields(self, request, obj=None):
        """Hacer que el campo es_activo sea de solo lectura a menos que sea superusuario"""
        if request.user.is_superuser:
            return ()
        return ('es_activo',)

    # Eliminamos la sección de Media ya que no tenemos CSS personalizado