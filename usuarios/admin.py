from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import PerfilUsuario

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfiles de Usuario'
    fk_name = 'user'
    fields = ('nombre_completo', 'numero_identificacion', 'fecha_nacimiento',
              'rm_snatch', 'rm_clean', 'rm_deadlift', 'rm_front_squat',
              'rm_back_squat', 'rm_press_banca')

class CustomUserAdmin(BaseUserAdmin):
    inlines = (PerfilUsuarioInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_nombre_completo_perfil')
    list_select_related = ('perfil',)

    def get_nombre_completo_perfil(self, instance):
        return instance.perfil.nombre_completo
    get_nombre_completo_perfil.short_description = 'Nombre Completo (Perfil)'

admin.site.unregister(User) # Desregistrar el UserAdmin por defecto
admin.site.register(User, CustomUserAdmin) # Registrar con nuestra personalización

# También puedes registrar PerfilUsuario por separado si prefieres
# @admin.register(PerfilUsuario)
# class PerfilUsuarioAdmin(admin.ModelAdmin):
#     list_display = ('user', 'nombre_completo', 'numero_identificacion', 'fecha_nacimiento')
#     search_fields = ('user__username', 'nombre_completo', 'numero_identificacion')