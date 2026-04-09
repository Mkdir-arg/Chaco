"""Paquete de vistas para la app de portal."""

from .public import (
    ConsultarTramiteView,
    CrearUsuarioInstitucionView,
    PortalHomeView,
    RegistroInstitucionView,
    get_localidades,
    get_municipios,
)


def crear_usuario_institucion(request):
    return CrearUsuarioInstitucionView.as_view()(request)


def registro_institucion(request):
    return RegistroInstitucionView.as_view()(request)


def consultar_tramite(request):
    return ConsultarTramiteView.as_view()(request)
