# usuarios/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views # Vistas de autenticación de Django
from . import views

urlpatterns = [
    path('registro/', views.registro_view, name='registro'),
    # Usamos la vista de login de Django por defecto, solo necesita la plantilla
    # path('login/', auth_views.LoginView.as_view(template_name='usuarios/login.html'), name='login'),
    # O usar la vista personalizada
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'), # Usamos nuestra vista para mensajes
    path('perfil/', views.ver_perfil_view, name='ver_perfil'),
    path('perfil/editar/', views.editar_perfil_view, name='editar_perfil'),

    # URLs para reseteo de contraseña (opcional pero recomendado)
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='usuarios/password_reset.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='usuarios/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='usuarios/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='usuarios/password_reset_complete.html'), name='password_reset_complete'),
]