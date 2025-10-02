# resultados/urls.py - ACTUALIZAR
from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_resultados, name='lista_resultados'),
    path('crear/', views.crear_resultado, name='crear_resultado'),
    path('editar/<int:pk>/', views.editar_resultado, name='editar_resultado'),
    path('eliminar/<int:pk>/', views.eliminar_resultado, name='eliminar_resultado'),
    path('publicos/', views.resultados_publicos, name='resultados_publicos'),
    
    # NUEVAS URLs PARA REACCIONES Y COMENTARIOS
    path('reaccionar/<int:resultado_id>/', views.toggle_reaccion, name='toggle_reaccion'),
    path('comentar/<int:resultado_id>/', views.agregar_comentario, name='agregar_comentario'),
    path('comentario/eliminar/<int:comentario_id>/', views.eliminar_comentario, name='eliminar_comentario'),
]