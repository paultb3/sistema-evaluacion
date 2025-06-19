from django.shortcuts import get_object_or_404, render
from apps.core.models import Curso
from apps.docentes.models import Docente
from apps.evaluacion.models import Evaluacion, Respuesta, ModuloPreguntas
from django.db.models import Avg

# Create your views here.


def bienvenido_docente(request, usuario_id):
    return render(request, 'bienvenido_docente.html', {'usuario_id': usuario_id })

def perfil_docente(request ,usuario_id):
    docente = get_object_or_404(Docente, usuario__id= usuario_id)
    
    
    curso = Curso.objects.all()
    print(curso)
    return render(request, 'perfil_docente.html', {'usuario_id': usuario_id , "docente":docente , "curso": curso})

def ver_recomendaciones(request, usuario_id):
    docente = get_object_or_404(Docente, usuario__id=usuario_id)
    
    # Obtener evaluaciones y módulos
    evaluaciones = Evaluacion.objects.filter(docente=docente, estado='enviada')
    modulos = ModuloPreguntas.objects.all()
    
    # Obtener puntuaciones por módulo
    recomendaciones = []
    for modulo in modulos:
        promedio = Respuesta.objects.filter(
            evaluacion__docente=docente,
            evaluacion__estado='enviada',
            pregunta__id_modulo=modulo
        ).aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
        
        # Generar recomendaciones basadas en el promedio
        if promedio < 3:
            recomendaciones.append({
                'modulo': modulo.nombre,
                'puntuacion': round(promedio, 1),
                'nivel': 'Bajo',
                'recomendaciones': [
                    'Considerar revisar y actualizar el material didáctico',
                    'Implementar más ejercicios prácticos',
                    'Solicitar retroalimentación específica a los estudiantes',
                    'Participar en talleres de desarrollo docente'
                ]
            })
        elif promedio < 4:
            recomendaciones.append({
                'modulo': modulo.nombre,
                'puntuacion': round(promedio, 1),
                'nivel': 'Medio',
                'recomendaciones': [
                    'Mantener las buenas prácticas actuales',
                    'Identificar áreas específicas de mejora',
                    'Compartir experiencias con otros docentes',
                    'Actualizar el material de estudio'
                ]
            })
        else:
            recomendaciones.append({
                'modulo': modulo.nombre,
                'puntuacion': round(promedio, 1),
                'nivel': 'Alto',
                'recomendaciones': [
                    'Compartir las mejores prácticas con otros docentes',
                    'Mantener el nivel de excelencia',
                    'Explorar nuevas metodologías de enseñanza',
                    'Mentorear a otros docentes'
                ]
            })
    
    context = {
        'usuario_id': usuario_id,
        'docente': docente,
        'recomendaciones': recomendaciones,
    }
    
    return render(request, 'ver_recomendaciones.html', context)

def ver_evaluacion(request, usuario_id):
    docente = get_object_or_404(Docente, usuario__id=usuario_id)
    
    # Obtener evaluaciones y módulos
    evaluaciones = Evaluacion.objects.filter(docente=docente, estado='enviada')
    modulos = ModuloPreguntas.objects.all()
    
    # Obtener puntuaciones por pregunta
    preguntas_con_puntuacion = []
    for modulo in modulos:
        for pregunta in modulo.preguntamodulo_set.all():
            promedio = Respuesta.objects.filter(
                evaluacion__docente=docente,
                evaluacion__estado='enviada',
                pregunta=pregunta
            ).aggregate(promedio=Avg('puntuacion'))['promedio'] or 0
            
            preguntas_con_puntuacion.append({
                'modulo': modulo,
                'pregunta': pregunta,
                'puntuacion': round(promedio, 1)
            })
    
    # Obtener comentarios
    comentarios = evaluaciones.filter(comentario_general__isnull=False).values_list('comentario_general', flat=True)
    
    context = {
        'usuario_id': usuario_id,
        'docente': docente,
        'evaluaciones': evaluaciones,
        'preguntas_con_puntuacion': preguntas_con_puntuacion,
        'comentarios': comentarios,
    }
    
    return render(request, 'ver_evaluacion.html', context)