from collections import defaultdict
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.db.models import Avg, Q
from apps.alumnos.models import Estudiante
from apps.core.models import Curso , Matricula
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
    cursos_matriculados = []
    matriculas = Matricula.objects.filter(estudiante=alumno).select_related('curso')
    
    # Obtener cursos matriculados
    for matricula in matriculas: 
        cursos_matriculados.append(matricula.curso)
    
    # Obtener número de evaluaciones realizadas por el alumno
    evaluaciones_count = Evaluacion.objects.filter(estudiante=alumno).count()
    
    # Obtener número de cursos que ha evaluado (distintos)
    cursos_evaluados = Evaluacion.objects.filter(estudiante=alumno).values('curso').distinct().count()
    
    print(f"Alumno encontrado: {alumno} con {len(cursos_matriculados)} cursos")
    return render(
        request, "perfil_alumno.html", {
            "usuario_id": usuario_id, 
            "alumno": alumno,
            "cursos": cursos_matriculados,
            "cursos_count": len(cursos_matriculados),
            "evaluaciones_count": evaluaciones_count,
            "cursos_evaluados": cursos_evaluados
        }
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
    
    # Obtener períodos de evaluación y la fecha actual
    from django.utils import timezone
    today = timezone.now().date()
    periodo = PeriodoEvaluacion.objects.all()
    
    # Verificar si hay un periodo activo
    periodo_activo = PeriodoEvaluacion.objects.filter(
        fecha_inicio__lte=today,
        fecha_fin__gte=today,
        estado='activo'
    ).exists()

    # Organizar preguntas por módulo
    modulo_dict = defaultdict(list)
    for pregunta in preguntas:
        modulo_dict[pregunta.id_modulo].append(pregunta)

    # Obtener solo los cursos en los que el estudiante está matriculado
    from apps.core.models import Matricula
    matriculas = Matricula.objects.filter(estudiante=alumno, estado='activa')
    cursos_disponibles = Curso.objects.filter(matricula__in=matriculas).distinct()

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
        "now": today,
        "periodo_activo": periodo_activo,
    }

    return render(request, "evaluar_docente.html", context)


def procesar_evaluacion(request, alumno):
    """Procesar el formulario de evaluación enviado"""
    
    try:        # Verificar si hay un periodo activo de evaluación
        from django.utils import timezone
        today = timezone.now().date()
        
        # Buscar si hay algún periodo de evaluación configurado
        periodos = PeriodoEvaluacion.objects.all()
        if not periodos.exists():
            messages.error(request, "No hay periodos de evaluación configurados en el sistema.")
            return redirect("alumno:evaluaciones", usuario_id=alumno.usuario.id)
        
        # Verificar si hay un periodo activo actual
        periodo_activo = PeriodoEvaluacion.objects.filter(
            fecha_inicio__lte=today,
            fecha_fin__gte=today,
            estado='activo'
        ).first()
        
        if not periodo_activo:
            # Verificar si el periodo finalizó o aún no comienza
            periodo_pasado = PeriodoEvaluacion.objects.filter(
                fecha_fin__lt=today
            ).order_by('-fecha_fin').first()
            
            periodo_futuro = PeriodoEvaluacion.objects.filter(
                fecha_inicio__gt=today
            ).order_by('fecha_inicio').first()
            
            if periodo_pasado:
                messages.error(request, f"El periodo de evaluación '{periodo_pasado.nombre}' ha finalizado el {periodo_pasado.fecha_fin}. No se pueden enviar más evaluaciones.")
            elif periodo_futuro:
                messages.error(request, f"El próximo periodo de evaluación '{periodo_futuro.nombre}' comenzará el {periodo_futuro.fecha_inicio}.")
            else:
                messages.error(request, "No hay un periodo de evaluación activo en este momento.")
                
            return redirect("alumno:evaluaciones", usuario_id=alumno.usuario.id)
            
        # Obtener datos del formulario
        curso_id = request.POST.get("curso_id")
        docente_id = request.POST.get("docente_id")

        if not curso_id or not docente_id:
            messages.error(request, "Debe seleccionar un curso y docente")
            return redirect("alumno:evaluaciones", usuario_id=alumno.usuario.id)

        curso = get_object_or_404(Curso, id=curso_id)
        docente = get_object_or_404(Docente, pk=docente_id)
        
        # Verificar que el estudiante está matriculado en este curso
        from apps.core.models import Matricula
        matricula_existe = Matricula.objects.filter(
            estudiante=alumno,
            curso=curso,
            estado='activa'
        ).exists()
        
        if not matricula_existe:
            messages.error(request, "No puede evaluar un curso en el que no está matriculado")
            return redirect("alumno:evaluaciones", usuario_id=alumno.usuario.id)

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
    """Vista para explorar docentes con sus evaluaciones"""
    query = request.GET.get("q", "")
    docentes = Docente.objects.all()

    # Obtener el estudiante
    alumno = get_object_or_404(Estudiante, usuario__id=usuario_id)
    
    # Obtener la lista de docentes que enseñan en cursos en los que el estudiante está matriculado
    from apps.core.models import Matricula
    docentes_evaluables_ids = Matricula.objects.filter(
        estudiante=alumno, 
        estado='activa'
    ).values_list('curso__docente', flat=True).distinct()

    if query:
        docentes = docentes.filter(
            Q(usuario__nombre__icontains=query) | Q(departamento__icontains=query)
        )
    data = []
    for docente in docentes:
        cursos = Curso.objects.filter(docente=docente)
        cursos_info = []
        total_puntuacion = 0
        cursos_evaluados = 0
        
        # Verificar si el estudiante puede evaluar a este docente
        docente.es_evaluable = docente.pk in docentes_evaluables_ids

        for curso in cursos:
            respuestas = Respuesta.objects.filter(
                evaluacion__curso=curso,
                evaluacion__docente=docente,
                evaluacion__estado="enviada",  # Asegurar que solo se consideren evaluaciones enviadas
            )
            promedio = respuestas.aggregate(prom=Avg("puntuacion"))["prom"]            # Contar cuántos estudiantes han evaluado este curso
            num_estudiantes = Evaluacion.objects.filter(
                curso=curso,
                docente=docente,
                estado="enviada"
            ).values('estudiante').distinct().count()
            
            # Determinar si el estudiante está matriculado en este curso específico
            curso.estudiante_matriculado = Matricula.objects.filter(
                estudiante=alumno,
                curso=curso,
                estado='activa'
            ).exists()
            
            # Almacenar la información del curso
            cursos_info.append(
                {
                    "curso": curso,
                    "promedio": promedio,
                    "respuestas": respuestas,
                    "num_estudiantes": num_estudiantes
                }
            )

            # Acumular para el promedio general si hay evaluaciones para este curso
            if promedio:
                total_puntuacion += float(promedio)
                cursos_evaluados += 1

        # Calcular el promedio general del docente
        promedio_general = None
        if cursos_evaluados > 0:
            promedio_general = round(total_puntuacion / cursos_evaluados, 2)

        # Preparar datos completos del docente
        docente_info = {
            "docente": docente,
            "cursos": cursos_info,
            "promedio_general": promedio_general,
            "cursos_evaluados": cursos_evaluados,
            "total_cursos": len(cursos_info),
            "es_evaluable": docente.es_evaluable,
        }

        data.append(docente_info)

    return render(
        request,
        "explorar.html",
        {
            "usuario_id": usuario_id,
            "data": data,
            "query": query,
            "alumno": alumno
        },
    )


def detalle_docente(request, usuario_id, docente_id):
    """Vista detallada de un docente con todas sus evaluaciones"""

    # Obtener el docente
    docente = get_object_or_404(Docente, usuario__id=docente_id)

    # Obtener todos los cursos impartidos por el docente
    cursos = Curso.objects.filter(docente=docente)

    cursos_info = []
    total_puntuacion = 0
    cursos_evaluados = 0

    # Obtener todas las respuestas de las evaluaciones del docente
    respuestas = Respuesta.objects.filter(
        evaluacion__docente=docente,
        evaluacion__estado="enviada",
    ).select_related("pregunta", "pregunta__id_modulo", "evaluacion", "evaluacion__curso")    # Procesar los cursos y sus evaluaciones
    for curso in cursos:
        curso_respuestas = respuestas.filter(evaluacion__curso=curso)
        promedio = curso_respuestas.aggregate(prom=Avg("puntuacion"))["prom"]
        
        # Contar cuántos estudiantes han evaluado este curso
        num_estudiantes = Evaluacion.objects.filter(
            curso=curso,
            docente=docente,
            estado="enviada"
        ).values('estudiante').distinct().count()

        cursos_info.append(
            {
                "curso": curso,
                "promedio": promedio,
                "respuestas": curso_respuestas,
                "num_estudiantes": num_estudiantes
            }
        )

        # Acumular para el promedio general
        if promedio:
            total_puntuacion += float(promedio)
            cursos_evaluados += 1

    # Calcular el promedio general
    promedio_general = round(total_puntuacion / cursos_evaluados, 2) if cursos_evaluados > 0 else None

    # Obtener los módulos y sus preguntas
    modulos = ModuloPreguntas.objects.all()

    # Diccionario para almacenar la puntuación por módulo y pregunta
    modulos_puntuacion = {}    # Procesar cada módulo y sus preguntas
    for modulo in modulos:
        preguntas_modulo = PreguntaModulo.objects.filter(id_modulo=modulo)
        preguntas_info = []
        total_puntuacion_modulo = 0
        preguntas_con_respuestas = 0
        
        for pregunta in preguntas_modulo:
            # Obtener las respuestas para esta pregunta específica
            pregunta_respuestas = respuestas.filter(pregunta=pregunta)
            promedio_pregunta = pregunta_respuestas.aggregate(prom=Avg("puntuacion"))["prom"]
            
            # Contar cuántos estudiantes han respondido esta pregunta
            num_estudiantes_pregunta = pregunta_respuestas.values('evaluacion__estudiante').distinct().count()

            if promedio_pregunta:
                preguntas_info.append(
                    {
                        "pregunta": pregunta,
                        "promedio": promedio_pregunta,
                        "respuestas": pregunta_respuestas,
                        "num_estudiantes": num_estudiantes_pregunta
                    }
                )
                total_puntuacion_modulo += float(promedio_pregunta)
                preguntas_con_respuestas += 1        # Solo incluir el módulo si tiene preguntas con respuestas
        if preguntas_con_respuestas > 0:
            promedio_modulo = round(total_puntuacion_modulo / preguntas_con_respuestas, 2)
            
            # Calcular el número total de estudiantes únicos que han evaluado este módulo
            estudiantes_modulo = set()
            for info in preguntas_info:
                for r in info["respuestas"]:
                    estudiantes_modulo.add(r.evaluacion.estudiante_id)
            
            modulos_puntuacion[modulo] = {
                "preguntas": preguntas_info,
                "promedio_modulo": promedio_modulo,
                "preguntas_con_respuestas": preguntas_con_respuestas,
                "num_estudiantes": len(estudiantes_modulo)
            }

    # Obtener comentarios generales (si existen)
    comentarios = Evaluacion.objects.filter(
        docente=docente,
        estado="enviada",
        comentario_general__isnull=False,
    ).exclude(comentario_general="").values("comentario_general", "fecha").order_by("-fecha")

    # Preparar la lista de comentarios si existen
    lista_comentarios = []
    for c in comentarios:
        lista_comentarios.append(
            {
                "texto": c["comentario_general"],
                "fecha": c.get("fecha"),
            }
        )

    context = {
        "usuario_id": usuario_id,
        "docente": docente,
        "cursos": cursos_info,
        "promedio_general": promedio_general,
        "cursos_evaluados": cursos_evaluados,
        "total_cursos": len(cursos_info),
        "modulos_puntuacion": modulos_puntuacion,
        "comentarios": lista_comentarios if lista_comentarios else None,
    }

    return render(request, "detalle_docente.html", context)
