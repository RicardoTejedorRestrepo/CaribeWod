from django.contrib import admin
from .models import ResultadoWOD, Reaccion, Comentario

@admin.register(Reaccion)
class ReaccionAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'resultado', 'tipo', 'fecha_creacion')
    list_filter = ('tipo', 'fecha_creacion')
    search_fields = ('usuario__username', 'resultado__usuario__username')
    date_hierarchy = 'fecha_creacion'

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'resultado', 'texto_corto', 'fecha_creacion')
    list_filter = ('fecha_creacion',)
    search_fields = ('usuario__username', 'texto', 'resultado__usuario__username')
    date_hierarchy = 'fecha_creacion'

@admin.register(ResultadoWOD)
class ResultadoWODAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha_wod', 'categoria', 'tiempo_formateado', 
                   'repeticiones', 'peso_total', 'unidad_peso', 'publico', 'fecha_creacion')
    list_filter = ('publico', 'categoria', 'fecha_wod', 'unidad_peso')
    search_fields = ('usuario__username', 'usuario__first_name', 'usuario__last_name', 'notas')
    list_editable = ('publico',)
    date_hierarchy = 'fecha_wod'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('usuario', 'fecha_wod', 'categoria', 'publico')
        }),
        ('Resultados', {
            'fields': ('tiempo_minutos', 'tiempo_segundos', 'repeticiones', 
                      'peso_total', 'unidad_peso')
        }),
        ('Notas', {
            'fields': ('notas',)
        }),
    )