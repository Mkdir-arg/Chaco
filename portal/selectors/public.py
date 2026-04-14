from core.models import Institucion
from legajos.models import Ciudadano
from legajos.models_programas import InscripcionPrograma, Programa


def get_portal_home_context():
    return {
        "programas": Programa.objects.filter(estado='ACTIVO').order_by("orden"),
        "instituciones": Institucion.objects.all()[:6],
        "stats": {
            "ciudadanos": Ciudadano.objects.count(),
            "instituciones": Institucion.objects.count(),
            "programas": Programa.objects.filter(estado='ACTIVO').count(),
            "inscripciones_activas": InscripcionPrograma.objects.filter(
                estado__in=["ACTIVO", "EN_SEGUIMIENTO"]
            ).count(),
        },
        "ciudadano_items": [
            "Mis programas sociales e inscripciones",
            "Consultas y reclamos municipales",
            "Mis datos personales y contraseña",
        ],
        "institucion_items": [
            "Registro guiado paso a paso",
            "Seguimiento del estado del trámite",
            "Articulación con programas municipales",
            "Mesa de ayuda especializada",
        ],
    }


def get_tramites_by_email(email):
    return Institucion.objects.filter(encargados__email=email).select_related(
        "provincia", "municipio", "localidad"
    )
