from django.shortcuts import get_object_or_404, render
from apps.core.models import Curso
from apps.docentes.models import Docente
from apps.evaluacion.models import Evaluacion, Respuesta, ModuloPreguntas
from django.db.models import Avg
from apps.core.models import Matricula

# Create your views here.


def bienvenido_docente(request, usuario_id):
    return render(request, "bienvenido_docente.html", {"usuario_id": usuario_id})


def perfil_docente(request, usuario_id):
    # Obtener el docente o devolver 404 si no existe
    docente = get_object_or_404(Docente, usuario__id=usuario_id)

    # Obtener todos los cursos del docente
    cursos = Curso.objects.filter(docente=docente)

    # Contar estudiantes matriculados de forma eficiente
    # Usamos count() en lugar de iterar manualmente
    estudiantes_totales = Matricula.objects.filter(curso_id__in=cursos).count()
    print(estudiantes_totales)
    return render(
        request,
        "perfil_docente.html",
        {
            "usuario_id": usuario_id,
            "docente": docente,
            "cursos": cursos,  # Renombrado para mayor claridad
            "estudiante_total": estudiantes_totales,
        },
    )


def ver_recomendaciones(request, usuario_id):
    docente = get_object_or_404(Docente, usuario__id=usuario_id)

    # Obtener evaluaciones y módulos
    evaluaciones = Evaluacion.objects.filter(docente=docente, estado="enviada")
    modulos = ModuloPreguntas.objects.all()

    # Obtener puntuaciones por módulo
    recomendaciones = []
    for modulo in modulos:
        promedio = (
            Respuesta.objects.filter(
                evaluacion__docente=docente,
                evaluacion__estado="enviada",
                pregunta__id_modulo=modulo,
            ).aggregate(promedio=Avg("puntuacion"))["promedio"]
            or 0
        )

        # Generar recomendaciones basadas en el promedio
        if promedio < 3:
            recomendaciones.append(
                {
                    "modulo": modulo.nombre,
                    "puntuacion": round(promedio, 1),
                    "nivel": "Bajo",
                    "recomendaciones": [
                        "Considerar revisar y actualizar el material didáctico",
                        "Implementar más ejercicios prácticos",
                        "Solicitar retroalimentación específica a los estudiantes",
                        "Participar en talleres de desarrollo docente",
                    ],
                }
            )
        elif promedio < 4:
            recomendaciones.append(
                {
                    "modulo": modulo.nombre,
                    "puntuacion": round(promedio, 1),
                    "nivel": "Medio",
                    "recomendaciones": [
                        "Mantener las buenas prácticas actuales",
                        "Identificar áreas específicas de mejora",
                        "Compartir experiencias con otros docentes",
                        "Actualizar el material de estudio",
                    ],
                }
            )
        else:
            recomendaciones.append(
                {
                    "modulo": modulo.nombre,
                    "puntuacion": round(promedio, 1),
                    "nivel": "Alto",
                    "recomendaciones": [
                        "Compartir las mejores prácticas con otros docentes",
                        "Mantener el nivel de excelencia",
                        "Explorar nuevas metodologías de enseñanza",
                        "Mentorear a otros docentes",
                    ],
                }
            )

    context = {
        "usuario_id": usuario_id,
        "docente": docente,
        "recomendaciones": recomendaciones,
    }

    return render(request, "ver_recomendaciones.html", context)


def ver_evaluacion(request, usuario_id):
    docente = get_object_or_404(Docente, usuario__id=usuario_id)

    # Obtener evaluaciones y módulos
    evaluaciones = Evaluacion.objects.filter(docente=docente, estado="enviada")
    modulos = ModuloPreguntas.objects.all()

    # Contar estudiantes únicos que evaluaron al docente
    total_estudiantes = evaluaciones.values("estudiante").distinct().count()

    # Obtener puntuaciones por pregunta
    preguntas_con_puntuacion = []
    for modulo in modulos:
        for pregunta in modulo.preguntamodulo_set.all():
            respuestas = Respuesta.objects.filter(
                evaluacion__docente=docente,
                evaluacion__estado="enviada",
                pregunta=pregunta,
            )
            promedio = respuestas.aggregate(promedio=Avg("puntuacion"))["promedio"] or 0

            # Contar estudiantes únicos que evaluaron esta pregunta
            num_estudiantes = (
                respuestas.values("evaluacion__estudiante").distinct().count()
            )

            preguntas_con_puntuacion.append(
                {
                    "modulo": modulo,
                    "pregunta": pregunta,
                    "puntuacion": round(promedio, 1),
                    "num_estudiantes": num_estudiantes,
                }
            )

    # Agrupar preguntas por módulo para una mejor visualización
    modulos_con_preguntas = {}
    for item in preguntas_con_puntuacion:
        modulo_id = str(item["modulo"].id_modulo)
        if modulo_id not in modulos_con_preguntas:
            modulos_con_preguntas[modulo_id] = {
                "modulo": item["modulo"],
                "preguntas": [],
                "promedio_modulo": 0,
                "num_estudiantes_modulo": 0,
            }
        modulos_con_preguntas[modulo_id]["preguntas"].append(item)

    # Calcular promedio por módulo
    for modulo_id, datos in modulos_con_preguntas.items():
        if datos["preguntas"]:
            # Calcular promedio del módulo
            suma_puntuaciones = sum(
                pregunta["puntuacion"] for pregunta in datos["preguntas"]
            )
            datos["promedio_modulo"] = round(
                suma_puntuaciones / len(datos["preguntas"]), 1
            )

            # Encontrar el máximo número de estudiantes que evaluaron cualquier pregunta del módulo
            datos["num_estudiantes_modulo"] = max(
                pregunta["num_estudiantes"] for pregunta in datos["preguntas"]
            )

    # Obtener comentarios
    comentarios = evaluaciones.filter(comentario_general__isnull=False).values_list(
        "comentario_general", flat=True
    )

    context = {
        "usuario_id": usuario_id,
        "docente": docente,
        "evaluaciones": evaluaciones,
        "preguntas_con_puntuacion": preguntas_con_puntuacion,
        "modulos_con_preguntas": modulos_con_preguntas,
        "comentarios": comentarios,
        "total_estudiantes": total_estudiantes,
    }

    return render(request, "ver_evaluacion.html", context)
