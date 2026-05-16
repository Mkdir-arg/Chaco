from django.http import HttpResponseGone
from django.views import View


def _deprecated_response():
    return HttpResponseGone(
        "DEPRECATED: configuracion.views.clases retirado con limpieza legacy."
    )


class ClaseListView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class ClaseCreateView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class ClaseEditarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class ClaseEliminarView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()


class ClaseAsistenciaView(View):
    def dispatch(self, request, *args, **kwargs):
        return _deprecated_response()
