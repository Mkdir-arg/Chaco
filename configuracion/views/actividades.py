from django.http import HttpResponseGone, JsonResponse
from django.views import View


def _deprecated_response():
    return HttpResponseGone(
        "DEPRECATED: configuracion.views.actividades retirado con limpieza legacy."
    )


class ActividadDetailView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class StaffActividadCreateView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class DerivacionAceptarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class DerivacionRechazarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class InscriptoEditarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class ActividadEditarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class InscripcionDirectaView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


def buscar_personal_ajax(request, actividad_pk):
    return JsonResponse(
        {
            "results": [],
            "error": "DEPRECATED: endpoint retirado con limpieza legacy.",
        },
        status=410,
    )
