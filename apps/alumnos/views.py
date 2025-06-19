from collections import defaultdict
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Avg, Q
from apps.alumnos.models import Estudiante
from apps.core.models import Curso
from apps.docentes.models import Docente
from apps.evaluacion.models import (
    Evaluacion,
    ModuloPreguntas,
    PreguntaModulo,
    Respuesta,
)
from apps.evaluacion.models import PeriodoEvaluacion


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
    periodo = PeriodoEvaluacion.objects.all()

    print(periodo)

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
        "cursos_disponibles": cursos_disponibles,
        "evaluaciones_existentes": evaluaciones_existentes,
        "periodo": periodo,
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
            return redirect("alumno:evaluaciones", usuario_id=alumno.usuario.id)

        curso = get_object_or_404(Curso, id=curso_id)
        docente = get_object_or_404(Docente, pk=docente_id)

        # Crear o obtener la evaluación principal
        evaluacion, created = Evaluacion.objects.get_or_create(
            estudiante=alumno,
            curso=curso,
            docente=docente,
            defaults={
                "estado": "enviada",
                "comentario_general": request.POST.get("comentario_general", ""),
            },
        )

        # Si la evaluación ya existía, actualizar el comentario general
        if not created:
            evaluacion.comentario_general = request.POST.get("comentario_general", "")
            evaluacion.save()

        # Obtener todas las preguntas
        preguntas = PreguntaModulo.objects.all()
        respuestas_creadas = 0
        respuestas_actualizadas = 0

        # Mapeo de valores numéricos a texto descriptivo
        criterio_texto = {
            "1": "Muy Deficiente",
            "2": "Deficiente",
            "3": "Regular",
            "4": "Bueno",
            "5": "Excelente",
        }

        for pregunta in preguntas:
            criterio_valor = request.POST.get(f"pregunta_{pregunta.id_pregunta}")
            print(
                f"Procesando pregunta {pregunta.id_pregunta}, criterio recibido: {criterio_valor}"
            )

            if criterio_valor:
                try:
                    # Obtener el texto descriptivo del criterio
                    criterio_texto_valor = criterio_texto.get(
                        criterio_valor, "Sin calificar"
                    )

                    # Crear o actualizar la respuesta
                    respuesta, created = evaluacion.respuestas.get_or_create(
                        pregunta=pregunta,
                        defaults={
                            "criterio": criterio_texto_valor,
                            "puntuacion": int(criterio_valor),
                        },
                    )

                    if not created:
                        respuesta.criterio = criterio_texto_valor
                        respuesta.puntuacion = int(criterio_valor)
                        respuesta.save()
                        respuestas_actualizadas += 1
                        print(
                            f"Respuesta actualizada para pregunta {pregunta.id_pregunta}"
                        )
                    else:
                        respuestas_creadas += 1
                        print(
                            f"Nueva respuesta creada para pregunta {pregunta.id_pregunta}"
                        )
                except Exception as e:
                    print(f"Error procesando pregunta {pregunta.id_pregunta}: {str(e)}")
                    messages.error(request, f"Error procesando la pregunta: {str(e)}")

        messages.success(
            request,
            f"Evaluación completada exitosamente. Nuevas respuestas: {respuestas_creadas}, actualizadas: {respuestas_actualizadas}.",
        )
    except Exception as e:
        print(f"Error general en procesar_evaluacion: {str(e)}")
        messages.error(request, f"Error al procesar la evaluación: {str(e)}")

    return redirect("alumno:evaluaciones", usuario_id=alumno.usuario.id)


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
    query = request.GET.get("q", "")
    docentes = Docente.objects.all()
    if query:
        docentes = docentes.filter(
            Q(usuario__nombre__icontains=query) | Q(departamento__icontains=query)
        )
    data = []
    for docente in docentes:
        cursos = Curso.objects.filter(docente=docente)
        cursos_info = []
        for curso in cursos:
            respuestas = Respuesta.objects.filter(
                evaluacion__curso=curso, evaluacion__docente=docente
            )
            promedio = respuestas.aggregate(prom=Avg("puntuacion"))["prom"]
            cursos_info.append(
                {
                    "curso": curso,
                    "promedio": promedio,
                    "respuestas": respuestas,
                }
            )
        # Asegúrate de agregar el docente aunque no tenga cursos
        data.append({"docente": docente, "cursos": cursos_info})
    print("DATA ARMADA:", data)  # <-- Agrega esto para depurar
    return render(
        request,
        "explorar.html",
        {
            "usuario_id": usuario_id,
            "data": data,
            "query": query,
        },
    )
