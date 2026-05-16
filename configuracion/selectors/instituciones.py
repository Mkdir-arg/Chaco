from django.db.models import Q
from legajos.models import Derivacion
from legajos.models_programas import Programa


def get_instituciones_queryset_for_user(user, search=""):
    return []


def build_institucion_detail_context(institucion):
    # Contexto simplificado tras retiro de modelos institucionales legacy.
    planes = Programa.objects.none()

    solapas = [
        {
            "id": "resumen",
            "nombre": "Resumen",
            "icono": "dashboard",
            "color": None,
            "estatica": True,
            "orden": 0,
        },
        {
            "id": "actividades",
            "nombre": "Actividades",
            "icono": "event",
            "color": None,
            "estatica": True,
            "orden": 25,
            "badge": 0,
        },
    ]

    return {
        "solapas": solapas,
        "personal": [],
        "evaluaciones": [],
        "planes": planes,
        "indicadores": [],
        "total_programas_activos": 0,
        "total_derivaciones_pendientes": 0,
        "total_casos_activos": 0,
    }


def build_actividad_detail_context(actividad):
    derivaciones = Derivacion.objects.filter(
        actividad_destino=actividad,
    ).exclude(estado="ACEPTADA").select_related(
        "legajo",
        "actividad_destino",
    ).order_by("-creado")

    return {
        "staff": [],
        "derivaciones": derivaciones,
        "nomina": [],
        "total_staff_activo": 0,
        "total_inscriptos_activos": 0,
        "cupo_disponible": True,
        "cupos_restantes": None,
    }


def search_personal_for_actividad(actividad, query=""):
    return []
