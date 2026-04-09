from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone

from ..models import Derivacion, EventoCritico, LegajoAtencion, SeguimientoContacto


def get_legajos_queryset(estado=""):
    queryset = LegajoAtencion.objects.select_related(
        'ciudadano',
        'dispositivo',
        'responsable',
    )
    if estado:
        queryset = queryset.filter(estado=estado)
    return queryset.order_by('-fecha_apertura')


def get_legajo_detail_queryset():
    return LegajoAtencion.objects.select_related(
        'ciudadano',
        'dispositivo',
        'responsable',
        'evaluacion',
    ).prefetch_related(
        'seguimientos__profesional__usuario',
        'eventos',
    )


def get_planes_queryset(legajo):
    return legajo.planes.select_related('profesional__usuario').order_by('-creado')


def get_plan_vigente(legajo):
    return legajo.planes.filter(vigente=True).select_related('profesional__usuario').first()


def get_seguimientos_queryset(legajo, tipo=""):
    queryset = legajo.seguimientos.select_related('profesional__usuario')
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    return queryset


def get_seguimientos_dashboard_metrics(legajo):
    return legajo.seguimientos.aggregate(
        total_seguimientos=Count('id'),
        entrevistas_count=Count('id', filter=Q(tipo='ENTREVISTA')),
        visitas_count=Count('id', filter=Q(tipo='VISITA')),
        llamadas_count=Count('id', filter=Q(tipo='LLAMADA')),
    )


def get_derivaciones_queryset(legajo, estado=""):
    queryset = legajo.derivaciones.select_related('destino', 'actividad_destino')
    if estado:
        queryset = queryset.filter(estado=estado)
    return queryset


def get_eventos_queryset(legajo, tipo=""):
    queryset = legajo.eventos.all()
    if tipo:
        queryset = queryset.filter(tipo=tipo)
    return queryset.order_by('-creado')


def get_eventos_dashboard_metrics(legajo):
    return legajo.eventos.aggregate(
        total_eventos=Count('id'),
        sobredosis_count=Count('id', filter=Q(tipo='SOBREDOSIS')),
        crisis_count=Count('id', filter=Q(tipo='CRISIS')),
        violencia_count=Count('id', filter=Q(tipo='VIOLENCIA')),
        internacion_count=Count('id', filter=Q(tipo='INTERNACION')),
    )


def get_dispositivo_derivaciones_queryset(dispositivo, estado=""):
    queryset = dispositivo.derivaciones_destino.select_related('legajo__ciudadano')
    if estado:
        queryset = queryset.filter(estado=estado)
    return queryset.order_by('-creado')


def get_export_legajos_queryset(estado="", riesgo=""):
    queryset = LegajoAtencion.objects.select_related('ciudadano', 'dispositivo')
    if estado:
        queryset = queryset.filter(estado=estado)
    if riesgo:
        queryset = queryset.filter(nivel_riesgo=riesgo)
    return queryset.order_by('-fecha_apertura')


def get_legajos_report_stats():
    fecha_limite = timezone.localdate() - timedelta(days=180)
    semana_actual = timezone.localdate() - timedelta(days=7)

    total_legajos = LegajoAtencion.objects.count()
    legajos_con_seguimiento = LegajoAtencion.objects.filter(
        seguimientos__isnull=False
    ).distinct()
    total_seguimientos = SeguimientoContacto.objects.count()
    total_derivaciones = Derivacion.objects.count()
    total_eventos = EventoCritico.objects.count()

    tiempos_primer_contacto = [
        tiempo
        for tiempo in (
            legajo.tiempo_primer_contacto
            for legajo in legajos_con_seguimiento
        )
        if tiempo is not None
    ]

    por_estado = [
        {
            'codigo': item['estado'],
            'label': dict(LegajoAtencion.Estado.choices).get(item['estado'], item['estado']),
            'total': item['total'],
        }
        for item in LegajoAtencion.objects.values('estado').annotate(total=Count('id')).order_by('-total')
    ]
    por_riesgo = [
        {
            'codigo': item['nivel_riesgo'],
            'label': dict(LegajoAtencion.NivelRiesgo.choices).get(item['nivel_riesgo'], item['nivel_riesgo']),
            'total': item['total'],
        }
        for item in LegajoAtencion.objects.values('nivel_riesgo').annotate(total=Count('id')).order_by('-total')
    ]

    por_dispositivo_raw = LegajoAtencion.objects.select_related('dispositivo').values(
        'dispositivo__nombre',
        'dispositivo__tipo',
    ).annotate(total=Count('id')).order_by('-total')[:10]

    return {
        'total_legajos': total_legajos,
        'legajos_activos': LegajoAtencion.objects.filter(
            estado__in=[
                    LegajoAtencion.Estado.ABIERTO,
                    LegajoAtencion.Estado.EN_SEGUIMIENTO,
                ]
        ).count(),
        'riesgo_alto': LegajoAtencion.objects.filter(
            nivel_riesgo=LegajoAtencion.NivelRiesgo.ALTO
        ).count(),
        'nuevos_semana': LegajoAtencion.objects.filter(
            fecha_apertura__gte=semana_actual
        ).count(),
        'por_estado': por_estado,
        'por_riesgo': por_riesgo,
        'por_dispositivo': [
            {
                'nombre': item['dispositivo__nombre'],
                'tipo_label': item['dispositivo__tipo'],
                'total': item['total'],
            }
            for item in por_dispositivo_raw
        ],
        'por_mes': LegajoAtencion.objects.filter(
            fecha_apertura__gte=fecha_limite
        ).annotate(
            mes=TruncMonth('fecha_apertura')
        ).values('mes').annotate(total=Count('id')).order_by('-mes')[:6],
        'metricas_calidad': {
            'ttr_promedio': round(sum(tiempos_primer_contacto) / len(tiempos_primer_contacto), 1) if tiempos_primer_contacto else 0,
            'adherencia_adecuada': round(
                (
                    SeguimientoContacto.objects.filter(adherencia='ADECUADA').count()
                    / max(total_seguimientos, 1)
                ) * 100,
                1,
            ),
            'tasa_derivacion': round(
                (
                    Derivacion.objects.filter(estado='ACEPTADA').count()
                    / max(total_derivaciones, 1)
                ) * 100,
                1,
            ),
            'eventos_por_100': round((total_eventos / max(total_legajos, 1)) * 100, 1),
            'cobertura_seguimiento': round(
                (legajos_con_seguimiento.count() / max(total_legajos, 1)) * 100,
                1,
            ),
        },
    }


def get_responsable_candidates():
    return [
        {
            'id': usuario.id,
            'nombre': usuario.get_full_name() or usuario.username,
        }
        for usuario in User.objects.filter(is_active=True).order_by(
            'first_name',
            'last_name',
            'username',
        )
    ]
