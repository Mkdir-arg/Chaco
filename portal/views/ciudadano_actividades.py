from django.http import HttpResponseGone

from core.decorators import ciudadano_required


def _deprecated_response():
    return HttpResponseGone(
        "DEPRECATED: flujo de actividades ciudadano retirado con limpieza legacy."
    )


@ciudadano_required
def ciudadano_mis_actividades(request):
    return _deprecated_response()


@ciudadano_required
def ciudadano_inscribirse_actividad(request, actividad_pk):
    return _deprecated_response()


@ciudadano_required
def ciudadano_detalle_actividad(request, actividad_pk):
    return _deprecated_response()
