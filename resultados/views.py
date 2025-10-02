from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.http import JsonResponse
from django.db import models  # IMPORTACIÓN AGREGADA
from .models import ResultadoWOD, Reaccion, Comentario
from .forms import ResultadoWODForm, ComentarioForm

@login_required
def toggle_reaccion(request, resultado_id):
    if request.method == 'POST':
        resultado = get_object_or_404(ResultadoWOD, id=resultado_id, publico=True)
        tipo_reaccion = request.POST.get('tipo')
        
        # Validar tipo de reacción
        tipos_validos = [tipo[0] for tipo in Reaccion.TIPO_REACCIONES]
        if tipo_reaccion not in tipos_validos:
            return JsonResponse({'success': False, 'error': 'Tipo de reacción inválido'})
        
        # Verificar si ya existe una reacción del usuario
        reaccion_existente = Reaccion.objects.filter(
            resultado=resultado, 
            usuario=request.user
        ).first()
        
        if reaccion_existente:
            if reaccion_existente.tipo == tipo_reaccion:
                # Si es la misma reacción, eliminarla (toggle)
                reaccion_existente.delete()
                accion = 'eliminada'
            else:
                # Si es diferente, actualizar
                reaccion_existente.tipo = tipo_reaccion
                reaccion_existente.save()
                accion = 'actualizada'
        else:
            # Crear nueva reacción
            Reaccion.objects.create(
                resultado=resultado,
                usuario=request.user,
                tipo=tipo_reaccion
            )
            accion = 'agregada'
        
        # Obtener conteos actualizados
        total_reacciones = resultado.reacciones.count()
        reacciones_por_tipo = resultado.reacciones.values('tipo').annotate(total=models.Count('tipo'))
        
        # Obtener el tipo de reacción del usuario actual después de la operación
        reaccion_actual = resultado.reacciones.filter(usuario=request.user).first()
        tipo_reaccion_usuario = reaccion_actual.tipo if reaccion_actual else None
        
        return JsonResponse({
            'success': True,
            'accion': accion,
            'total_reacciones': total_reacciones,
            'reacciones_por_tipo': list(reacciones_por_tipo),
            'usuario_ha_reaccionado': resultado.usuario_ha_reaccionado(request.user),
            'tipo_reaccion_usuario': tipo_reaccion_usuario
        })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def agregar_comentario(request, resultado_id):
    if request.method == 'POST':
        resultado = get_object_or_404(ResultadoWOD, id=resultado_id, publico=True)
        form = ComentarioForm(request.POST)
        
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.resultado = resultado
            comentario.usuario = request.user
            comentario.save()
            
            # Devolver datos del comentario para actualizar la UI
            return JsonResponse({
                'success': True,
                'comentario': {
                    'id': comentario.id,
                    'usuario': comentario.usuario.username,
                    'nombre_completo': comentario.usuario.get_full_name() or comentario.usuario.username,
                    'texto': comentario.texto,
                    'fecha_creacion': comentario.fecha_creacion.strftime('%d/%m/%Y %H:%M'),
                    'fecha_actualizacion': comentario.fecha_actualizacion.strftime('%d/%m/%Y %H:%M')
                }
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

@login_required
def eliminar_comentario(request, comentario_id):
    if request.method == 'POST':
        comentario = get_object_or_404(Comentario, id=comentario_id)
        
        # Verificar que el usuario es el dueño del comentario
        if comentario.usuario != request.user:
            return JsonResponse({'success': False, 'error': 'No tienes permiso para eliminar este comentario'})
        
        comentario.delete()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})


@login_required
def lista_resultados(request):
    # Obtener parámetros de filtro
    fecha_filtro = request.GET.get('fecha', '')
    ver_todos = request.GET.get('todos', 'false') == 'true'
    ordenar_por = request.GET.get('ordenar', '-fecha_wod')
    direccion = request.GET.get('dir', 'desc')
    
    # Base queryset
    resultados = ResultadoWOD.objects.filter(usuario=request.user)
    resultados = resultados.select_related('usuario').prefetch_related(
        'reacciones', 'reacciones__usuario', 'comentarios', 'comentarios__usuario'
    )
    
    # Aplicar filtro de fecha si se especificó
    if fecha_filtro and not ver_todos:
        try:
            fecha = date.fromisoformat(fecha_filtro)
            resultados = resultados.filter(fecha_wod=fecha)
        except ValueError:
            # Si la fecha no es válida, ignorar el filtro
            pass
    # Si no se especifica fecha y no se piden todos, mostrar solo los de hoy
    elif not ver_todos:
        resultados = resultados.filter(fecha_wod=date.today())
    
    # Aplicar ordenamiento
    if ordenar_por == 'tiempo':
        if direccion == 'asc':
            resultados = resultados.order_by('tiempo_minutos', 'tiempo_segundos')
        else:
            resultados = resultados.order_by('-tiempo_minutos', '-tiempo_segundos')
    elif ordenar_por == 'repeticiones':
        if direccion == 'asc':
            resultados = resultados.order_by('repeticiones')
        else:
            resultados = resultados.order_by('-repeticiones')
    elif ordenar_por == 'peso':
        if direccion == 'asc':
            resultados = resultados.order_by('peso_total')
        else:
            resultados = resultados.order_by('-peso_total')
    elif ordenar_por == 'fecha':
        if direccion == 'asc':
            resultados = resultados.order_by('fecha_wod')
        else:
            resultados = resultados.order_by('-fecha_wod')
    elif ordenar_por == 'categoria':
        if direccion == 'asc':
            resultados = resultados.order_by('categoria')
        else:
            resultados = resultados.order_by('-categoria')
    else:  # Por defecto ordenar por fecha descendente
        resultados = resultados.order_by('-fecha_wod', '-fecha_creacion')
    
    context = {
        'resultados': resultados,
        'fecha_filtro': fecha_filtro,
        'ver_todos': ver_todos,
        'ordenar_por': ordenar_por,
        'direccion': direccion,
    }
    return render(request, 'resultados/lista_resultados.html', context)

def resultados_publicos(request):
    # Obtener parámetros de filtro
    fecha_filtro = request.GET.get('fecha', '')
    categoria_filtro = request.GET.getlist('categoria')  # Múltiples categorías
    ordenar_por = request.GET.get('ordenar', '-fecha_wod')
    direccion = request.GET.get('dir', 'desc')
    buscar = request.GET.get('buscar', '')
    
    # Base queryset - solo resultados públicos
    resultados = ResultadoWOD.objects.filter(publico=True).select_related('usuario')
    
    if request.user.is_authenticated:
        # Prefetch reacciones y comentarios para optimización
        resultados = resultados.prefetch_related(
            'reacciones', 'comentarios', 'comentarios__usuario'
        )
    
    # Aplicar filtro de fecha
    if fecha_filtro:
        try:
            fecha = date.fromisoformat(fecha_filtro)
            resultados = resultados.filter(fecha_wod=fecha)
        except ValueError:
            # Si la fecha no es válida, mostrar todos los públicos
            pass
    else:
        # Por defecto, mostrar resultados del día actual
        resultados = resultados.filter(fecha_wod=date.today())
    
    # Aplicar filtro de categoría
    if categoria_filtro:
        resultados = resultados.filter(categoria__in=categoria_filtro)
    
    # Aplicar búsqueda por nombre de usuario
    if buscar:
        resultados = resultados.filter(
            usuario__username__icontains=buscar
        ) | resultados.filter(
            usuario__first_name__icontains=buscar
        ) | resultados.filter(
            usuario__last_name__icontains=buscar
        )
        
    # PRE-CALCULAR REACCIONES DEL USUARIO ACTUAL PARA CADA RESULTADO
    for resultado in resultados:
        if request.user.is_authenticated:
            # Obtener la reacción del usuario actual para este resultado
            user_reaction = resultado.get_reaccion_usuario(request.user)
            resultado.user_reaction_type = user_reaction.tipo if user_reaction else None
            
            # Flags individuales para cada tipo de reacción
            resultado.user_has_me_gusta = user_reaction and user_reaction.tipo == 'me_gusta'
            resultado.user_has_me_encanta = user_reaction and user_reaction.tipo == 'me_encanta'
            resultado.user_has_muy_fuerte = user_reaction and user_reaction.tipo == 'muy_fuerte'
            resultado.user_has_por_poco = user_reaction and user_reaction.tipo == 'por_poco'
        else:
            resultado.user_reaction_type = None
            resultado.user_has_me_gusta = False
            resultado.user_has_me_encanta = False
            resultado.user_has_muy_fuerte = False
            resultado.user_has_por_poco = False
    
    # Aplicar ordenamiento
    if ordenar_por == 'tiempo':
        if direccion == 'asc':
            resultados = resultados.order_by('tiempo_minutos', 'tiempo_segundos')
        else:
            resultados = resultados.order_by('-tiempo_minutos', '-tiempo_segundos')
    elif ordenar_por == 'repeticiones':
        if direccion == 'asc':
            resultados = resultados.order_by('repeticiones')
        else:
            resultados = resultados.order_by('-repeticiones')
    elif ordenar_por == 'peso':
        if direccion == 'asc':
            resultados = resultados.order_by('peso_total')
        else:
            resultados = resultados.order_by('-peso_total')
    elif ordenar_por == 'fecha':
        if direccion == 'asc':
            resultados = resultados.order_by('fecha_wod')
        else:
            resultados = resultados.order_by('-fecha_wod')
    elif ordenar_por == 'categoria':
        if direccion == 'asc':
            resultados = resultados.order_by('categoria')
        else:
            resultados = resultados.order_by('-categoria')
    elif ordenar_por == 'usuario':
        if direccion == 'asc':
            resultados = resultados.order_by('usuario__username')
        else:
            resultados = resultados.order_by('-usuario__username')
    else:  # fecha por defecto
        resultados = resultados.order_by('-fecha_wod', '-fecha_creacion')
    
    context = {
        'resultados': resultados,
        'fecha_filtro': fecha_filtro,
        'categoria_filtro': categoria_filtro,
        'ordenar_por': ordenar_por,
        'direccion': direccion,
        'buscar': buscar,
        'CATEGORIA_CHOICES': ResultadoWOD.CATEGORIA_CHOICES,
        'form_comentario': ComentarioForm(),
    }
    return render(request, 'resultados/resultados_publicos.html', context)

@login_required
def crear_resultado(request):
    if request.method == 'POST':
        form = ResultadoWODForm(request.POST)
        if form.is_valid():
            resultado = form.save(commit=False)
            resultado.usuario = request.user
            resultado.save()
            messages.success(request, '¡Resultado registrado exitosamente!')
            return redirect('lista_resultados')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ResultadoWODForm()
    
    return render(request, 'resultados/crear_resultado.html', {'form': form})

@login_required
def editar_resultado(request, pk):
    resultado = get_object_or_404(ResultadoWOD, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        form = ResultadoWODForm(request.POST, instance=resultado)
        if form.is_valid():
            resultado_editado = form.save(commit=False)
            resultado_editado.usuario = request.user
            resultado_editado.save()
            
            messages.success(request, '¡Resultado actualizado exitosamente!')
            return redirect('lista_resultados')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ResultadoWODForm(instance=resultado)
    
    return render(request, 'resultados/editar_resultado.html', {
        'form': form, 
        'resultado': resultado
    })
    
@login_required
def eliminar_resultado(request, pk):
    resultado = get_object_or_404(ResultadoWOD, pk=pk, usuario=request.user)
    
    if request.method == 'POST':
        resultado.delete()
        messages.success(request, '¡Resultado eliminado exitosamente!')
        return redirect('lista_resultados')
    
    return render(request, 'resultados/eliminar_resultado.html', {'resultado': resultado})