# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import RegistroUsuarioForm, PerfilUsuarioForm
from .models import PerfilUsuario
from django.contrib.auth.models import User

def registro_view(request):
    if request.user.is_authenticated:
        messages.info(request, 'Ya tienes una sesión activa.')
        return redirect('ver_perfil')

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, f'¡Bienvenido {user.username}! Registro exitoso.')
                    return redirect('editar_perfil')
            except Exception as e:
                messages.error(request, 'Ocurrió un error durante el registro. Por favor, intenta nuevamente.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = RegistroUsuarioForm()
    
    context = {
        'form': form,
        'title': 'Registro de Usuario'
    }
    return render(request, 'usuarios/registro.html', context)

from django.contrib.auth.views import LoginView as AuthLoginView

class CustomLoginView(AuthLoginView):
    template_name = 'usuarios/login.html'

    def form_valid(self, form):
        messages.success(self.request, f"¡Bienvenido de nuevo, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Credenciales incorrectas. Por favor, verifica tu usuario y contraseña.")
        return super().form_invalid(form)

@login_required
def logout_view(request):
    username = request.user.username
    logout(request)
    messages.info(request, f'Has cerrado sesión exitosamente. ¡Hasta pronto, {username}!')
    return redirect('home')

@login_required
def ver_perfil_view(request):
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(user=request.user)
        messages.info(request, 'Se ha creado tu perfil automáticamente.')
    
    context = {
        'perfil': perfil,
        'title': f'Perfil - {request.user.username}'
    }
    return render(request, 'usuarios/ver_perfil.html', context)

@login_required
def editar_perfil_view(request):
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        perfil = PerfilUsuario.objects.create(user=request.user)

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Guardar datos del perfil
                    perfil = form.save(commit=False)
                    perfil.user = request.user
                    perfil.save()
                    
                    # Actualizar datos del usuario
                    user = request.user
                    user.first_name = form.cleaned_data.get('first_name', '')
                    user.last_name = form.cleaned_data.get('last_name', '')
                    user.email = form.cleaned_data.get('email', '')
                    user.save()
                    
                    messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
                    return redirect('ver_perfil')
            except Exception as e:
                messages.error(request, 'Ocurrió un error al guardar los cambios. Por favor, intenta nuevamente.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PerfilUsuarioForm(instance=perfil)

    context = {
        'form': form,
        'title': 'Editar Perfil'
    }
    return render(request, 'usuarios/editar_perfil.html', context)