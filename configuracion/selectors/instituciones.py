from django.db.models import Count, Q

from core.models import Institucion
from legajos.models import (
    Derivacion,
    EvaluacionInstitucional,
    IndicadorInstitucional,
    InscriptoActividad,
    PersonalInstitucion,
    PlanFortalecimiento,
    StaffActividad,
)


def get_instituciones_queryset_for_user(user, search=""):
    if user.is_superuser:
        queryset = Institucion.objects.filter(
            estado_registro="APROBADO"
        )
    else:
        queryset = Institucion.objects.filter(
            encargados=user,
            estado_registro="APROBADO",
        )

    queryset = queryset.select_related(
        "provincia",
        "municipio",
        "localidad",
    ).prefetch_related("encargados")

    if search:
        queryset = queryset.filter(
            Q(nombre__icontains=search) | Q(cuit__icontains=search)
        )

    return queryset.order_by("nombre")


def build_institucion_detail_context(institucion):
    # DEPRECATED: legado SEDRONAR retirado (models_institucional eliminado).
    programas_activos = []
    planes = PlanFortalecimiento.objects.filter(
        legajo_institucional__institucion=institucion
    ).prefetch_related("staff__personal").order_by("-fecha_inicio")

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
            "badge": planes.count(),
        },
    ]

    solapas.sort(key=lambda item: item["orden"])

    return {
        "solapas": solapas,
        "personal": PersonalInstitucion.objects.filter(
            legajo_institucional__institucion=institucion
        ).select_related("legajo_institucional"),
        "evaluaciones": EvaluacionInstitucional.objects.filter(
            legajo_institucional__institucion=institucion
        ).select_related("evaluador").order_by("-fecha_evaluacion"),
        "planes": planes,
        "indicadores": IndicadorInstitucional.objects.filter(
            legajo_institucional__institucion=institucion
        ).select_related("legajo_institucional").order_by("-periodo"),
        "total_programas_activos": len(programas_activos),
        "total_derivaciones_pendientes": sum(
            item.get("badge_derivaciones", 0)
            for item in solapas
            if not item["estatica"]
        ),
        "total_casos_activos": sum(
            item.get("badge_casos", 0) for item in solapas if not item["estatica"]
        ),
    }


def build_actividad_detail_context(actividad):
    staff = StaffActividad.objects.filter(actividad=actividad).select_related(
        "personal",
        "actividad",
    )
    derivaciones = Derivacion.objects.filter(
        actividad_destino=actividad
    ).exclude(estado="ACEPTADA").select_related(
        "legajo__ciudadano",
        "destino",
    ).order_by("-creado")
    nomina = InscriptoActividad.objects.filter(actividad=actividad).select_related(
        "ciudadano",
        "actividad",
    ).annotate(
        cantidad_presentes=Count(
            "asistencias",
            filter=Q(asistencias__estado="PRESENTE"),
        ),
        cantidad_ausentes=Count(
            "asistencias",
            filter=Q(asistencias__estado="AUSENTE"),
        ),
    ).order_by("-fecha_inscripcion")

    total_activos = nomina.filter(estado__in=["INSCRITO", "ACTIVO"]).count()
    cupo = actividad.cupo_ciudadanos
    if cupo == 0:
        cupo_disponible = True
        cupos_restantes = None  # ilimitado
    else:
        cupo_disponible = total_activos < cupo
        cupos_restantes = max(0, cupo - total_activos)

    return {
        "staff": staff,
        "derivaciones": derivaciones,
        "nomina": nomina,
        "total_staff_activo": staff.filter(activo=True).count(),
        "total_inscriptos_activos": total_activos,
        "cupo_disponible": cupo_disponible,
        "cupos_restantes": cupos_restantes,
    }


def search_personal_for_actividad(actividad, query=""):
    personal = PersonalInstitucion.objects.filter(
        legajo_institucional=actividad.legajo_institucional,
        activo=True,
    )

    if query:
        personal = personal.filter(
            Q(nombre__icontains=query)
            | Q(apellido__icontains=query)
            | Q(dni__icontains=query)
        )

    return personal.order_by("apellido", "nombre")
