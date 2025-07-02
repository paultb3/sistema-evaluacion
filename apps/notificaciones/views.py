from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Notificaciones
from apps.usuarios.models import Usuario

# Create your views here.


def obtener_notificaciones(request, usuario_id):
    """
    Vista para obtener las notificaciones de un usuario específico.
    Se puede llamar via AJAX o como una vista normal.
    """
    usuario = get_object_or_404(Usuario, id=usuario_id)
    notificaciones = Notificaciones.objects.filter(usuario=usuario).order_by(
        "-fecha_creacion"
    )

    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        data = []
        for notif in notificaciones:
            data.append(
                {
                    "id": str(notif.id_notificaciones),
                    "tipo": notif.tipo,
                    "nombre": notif.nombre,
                    "estado": notif.estado,
                    "fecha": notif.fecha_creacion.strftime("%d-%m-%Y %H:%M"),
                }
            )
        return JsonResponse({"notificaciones": data})

    # Si no es AJAX, renderizar template
    # Determinar el tipo de usuario para elegir la plantilla base correcta
    template_base = "base/alumno.html"  # default

    try:
        from apps.alumnos.models import Estudiante
        from apps.docentes.models import Docente
        from apps.comision.models import Comision

        if Estudiante.objects.filter(usuario=usuario).exists():
            template_base = "base/alumno.html"
        elif Docente.objects.filter(usuario=usuario).exists():
            template_base = "base/docente.html"
        elif Comision.objects.filter(usuario=usuario).exists():
            template_base = "base/comision.html"
    except Exception as e:
        print(f"Error determinando tipo de usuario: {e}")

    return render(
        request,
        "notificaciones/lista_notificaciones.html",
        {
            "notificaciones": notificaciones,
            "usuario_id": usuario_id,
            "template_base": template_base,
        },
    )


def marcar_notificacion_leida(request, notificacion_id):
    """
    Vista para marcar una notificación como leída
    """
    notificacion = get_object_or_404(Notificaciones, id_notificaciones=notificacion_id)
    notificacion.estado = "leido"
    notificacion.save()

    # Si es una solicitud AJAX, devolver JSON
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"success": True})

    # Si no es AJAX, redirigir a la página anterior
    referer = request.META.get("HTTP_REFERER", "/")
    return redirect(referer)
