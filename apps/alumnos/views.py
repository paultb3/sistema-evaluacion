from collections import defaultdict
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from apps.alumnos.models import Estudiante
from apps.core.models import Curso
from apps.docentes.models import Docente
from apps.evaluacion.models import Criterio, Evaluacion, ModuloPreguntas, PreguntaModulo


def bienvenida_alumnos(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    return render(request, "bienvenida_alumno.html", {"usuario_id": usuario_id})


def perfil_alumno(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")

    alumno = get_object_or_404(Estudiante, usuario__id=usuario_id)

    print(f"Alumno encontrado: {alumno}")
    return render(
        request, "perfil_alumno.html", {"usuario_id": usuario_id, "alumno": alumno}
    )


def evaluar_docente(request, usuario_id):
    # Obtener el estudiante
    alumno = get_object_or_404(Estudiante, usuario__id=usuario_id)

    if request.method == "POST":
        return procesar_evaluacion(request, alumno)

    # GET → mostrar el formulario
    return mostrar_formulario_evaluacion(request, alumno, usuario_id)


def mostrar_formulario_evaluacion(request, alumno, usuario_id):
    """Mostrar el formulario de evaluación"""

    # Obtener todas las preguntas organizadas por módulo
    preguntas = PreguntaModulo.objects.select_related("id_modulo").all()
    modulos = ModuloPreguntas.objects.all()
    criterios = Criterio.objects.all()

    # Organizar preguntas por módulo
    modulo_dict = defaultdict(list)
    for pregunta in preguntas:
        modulo_dict[pregunta.id_modulo].append(pregunta)

    # Obtener cursos disponibles para evaluar
    cursos_disponibles = Curso.objects.all()

    # Verificar si el estudiante ya tiene evaluaciones
    evaluaciones_existentes = Evaluacion.objects.filter(estudiante=alumno)

    context = {
        "usuario_id": usuario_id,
        "alumno": alumno,
        "modulos": modulos,
        "modulo_dict": dict(modulo_dict),  # Convertir defaultdict a dict normal
        "criterios": criterios,
        "cursos_disponibles": cursos_disponibles,
        "evaluaciones_existentes": evaluaciones_existentes,
    }

    return render(request, "evaluar_docente.html", context)


def procesar_evaluacion(request, alumno):
    """Procesar el formulario de evaluación enviado"""

    try:
        # Obtener datos del formulario
        curso_id = request.POST.get("curso_id")
        docente_id = request.POST.get("docente_id")

        if not curso_id or not docente_id:
            messages.error(request, "Debe seleccionar un curso y docente")
            print(alumno.usuario.id)
            return redirect("alumno:evaluar_docente", usuario_id=alumno.usuario.id)

        curso = get_object_or_404(Curso, id=curso_id)
        docente = get_object_or_404(Docente, usuario=docente_id)
        print(curso, docente)

        # Procesar respuestas por pregunta
        preguntas = PreguntaModulo.objects.all()
        evaluaciones_creadas = 0
        print(preguntas)

        for pregunta in preguntas:
            # Obtener la respuesta para esta pregunta
            criterio_id = request.POST.get(f"pregunta_{pregunta.id_pregunta}")

            if criterio_id:
                criterio = get_object_or_404(Criterio, id=criterio_id)
                print(criterio)
                # Verificar si ya existe una evaluación para esta combinación
                evaluacion_existente = Evaluacion.objects.filter(
                    estudiante=alumno, curso=curso, docente=docente, pregunta=pregunta
                ).first()
                print(evaluacion_existente)
                if evaluacion_existente:
                    # Actualizar evaluación existente
                    evaluacion_existente.criterio = criterio
                    evaluacion_existente.save()
                else:
                    # Crear nueva evaluación
                    Evaluacion.objects.create(
                        estudiante=alumno,
                        curso=curso,
                        docente=docente,
                        pregunta=pregunta,
                        criterio=criterio,
                    )
                    evaluaciones_creadas += 1

        messages.success(
            request,
            f"Evaluación completada exitosamente. Se crearon {evaluaciones_creadas} nuevas respuestas.",
        )

    except Exception as e:
        messages.error(request, f"Error al procesar la evaluación: {str(e)}")

    return redirect("alumno:evaluar_docente", usuario_id=alumno.usuario.id)


# Vista adicional para obtener docentes por curso (AJAX)
def obtener_docentes_por_curso(request, curso_id):
    """Obtener docentes de un curso específico (para uso con AJAX)"""

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        try:
            curso = get_object_or_404(Curso, id=curso_id)
            docentes = [{"id": curso.docente.pk, "nombre": str(curso.docente)}]
            return JsonResponse({"docentes": docentes})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Petición no válida"}, status=400)


def explorar(request, usuario_id):
    print(f"Usuario recibido: {usuario_id}")
    modulo = PreguntaModulo.objects.all()

    context = {"modulo": modulo, "usuario_id": usuario_id}
    return render(
        request, "explorar.html", {"usuario_id": usuario_id, "modulo": modulo}
    )
