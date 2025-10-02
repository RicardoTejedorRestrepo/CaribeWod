# entrenamientos/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.mostrar_entrenamiento_view, name='mostrar_entrenamiento'),
    path('calculadora-porcentajes/', views.calculadora_porcentajes, name='calculadora_porcentajes'),
]