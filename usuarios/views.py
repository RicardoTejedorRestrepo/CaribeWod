# usuarios/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegistroUsuarioForm, PerfilUsuarioForm
from .models import PerfilUsuario

def registro_view(request):
    if request.user.is_authenticated:
        return redirect('ver_perfil') # O a donde quieras que vayan los ya logueados

    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            # nombre_completo = form.cleaned_data.get('nombre_completo')
            # if nombre_completo: # Si lo pediste en el form de registro
            #     user.perfil.nombre_completo = nombre_completo
            #     user.perfil.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Ahora puedes completar tu perfil.')
            return redirect('editar_perfil') # Redirige a la edición de perfil
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{form.fields[field].label}: {error}")
    else:
        form = RegistroUsuarioForm()
    return render(request, 'usuarios/registro.html', {'form': form})

# Django ya provee una vista de login, pero puedes personalizarla si es necesario.
# Si usas la de Django, solo necesitas la plantilla `registration/login.html`.
# Para una vista personalizada de login:
from django.contrib.auth.views import LoginView as AuthLoginView

class CustomLoginView(AuthLoginView):
    template_name = 'usuarios/login.html' # Tu plantilla personalizada
    # form_class = TuCustomAuthenticationForm si lo tienes

    def form_valid(self, form):
        messages.success(self.request, f"Bienvenido de nuevo, {form.get_user().username}!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Nombre de usuario o contraseña incorrectos.")
        return super().form_invalid(form)


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'Has cerrado sesión exitosamente.')
    return redirect('home') # Redirige a la página de inicio

@login_required
def ver_perfil_view(request):
    try:
        perfil = request.user.perfil
    except PerfilUsuario.DoesNotExist:
        # Esto no debería pasar si la señal funciona, pero es un fallback
        perfil = PerfilUsuario.objects.create(user=request.user)
    return render(request, 'usuarios/ver_perfil.html', {'perfil': perfil})

@login_required
def editar_perfil_view(request):
    perfil, created = PerfilUsuario.objects.get_or_create(user=request.user) # Asegura que el perfil exista

    if request.method == 'POST':
        form = PerfilUsuarioForm(request.POST, instance=perfil)
        # También podrías actualizar User.first_name y User.last_name
        user_form_data = {
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'email': request.POST.get('email'),
        }
        # Aquí podrías tener un UserChangeForm para actualizar datos del User model

        if form.is_valid():
            form.save()

            # Actualizar campos del modelo User si es necesario
            nombre_completo_form = form.cleaned_data.get('nombre_completo', '')
            if nombre_completo_form:
                partes_nombre = nombre_completo_form.split(' ', 1)
                request.user.first_name = partes_nombre[0]
                if len(partes_nombre) > 1:
                    request.user.last_name = partes_nombre[1]
                else:
                    request.user.last_name = '' # o dejarlo como estaba
                request.user.save()

            messages.success(request, '¡Tu perfil ha sido actualizado exitosamente!')
            return redirect('ver_perfil')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = PerfilUsuarioForm(instance=perfil)

    return render(request, 'usuarios/editar_perfil.html', {'form': form})