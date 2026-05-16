from django.http import HttpResponseGone
from django.views import View


def _deprecated_response():
    return HttpResponseGone(
        "DEPRECATED: configuracion.views.extra retirado con limpieza legacy."
    )


class StaffEditarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class StaffDesasignarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class AsistenciaView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class TomarAsistenciaView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class RegistrarAsistenciaView(TomarAsistenciaView):
    pass
