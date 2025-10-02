"""
URL configuration for caribe_wod_tracker project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cuentas/', include('usuarios.urls')),
    path('entrenamientos/', include('entrenamientos.urls')),
    path('resultados/', include('resultados.urls')),  # Nueva línea
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]