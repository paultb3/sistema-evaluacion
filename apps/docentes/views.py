from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Docente
from .forms import PerfilDocenteForm
from django.contrib.auth import logout

@login_required(login_url='core:login')
def dashboard_docente(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    evaluaciones = docente.evaluaciones.all()
    promedio = evaluaciones.aggregate_avg('puntuacion') if evaluaciones else 0
    total = evaluaciones.count()
    recientes = evaluaciones.order_by('-fecha')[:5]

    return render(request, 'docentes/dashboard.html', {
        'docente': docente,
        'promedio': round(promedio or 0, 2),
        'total': total,
        'recientes': recientes,
    })

@login_required(login_url='core:login')
def perfil_docente(request):
    docente = get_object_or_404(Docente, usuario=request.user)
    evaluaciones = docente.evaluaciones.all()
    return render(request, 'docentes/perfil.html', {
        'docente': docente,
        'evaluaciones': evaluaciones,
    })

@login_required(login_url='core:login')
def editar_perfil_docente(request):
    docente = get_object_or_404(Docente, usuario=request.user)

    if request.method == 'POST':
        form = PerfilDocenteForm(request.POST, instance=docente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('docentes:perfil')
    else:
        form = PerfilDocenteForm(instance=docente)

    return render(request, 'docentes/editar_perfil.html', {
        'form': form,
        'docente': docente,
    })

def logout_view(request):
    logout(request)
    return redirect('core:login')