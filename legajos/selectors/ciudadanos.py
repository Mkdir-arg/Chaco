from datetime import date

from django.db.models import Q

from ..models import Ciudadano, EventoCritico, LegajoAtencion, SeguimientoContacto
from ..models_nachec import (
    CasoNachec,
    EvaluacionVulnerabilidad,
    HistorialEstadoCaso,
    PlanIntervencionNachec,
    PrestacionNachec,
    RelevamientoNachec,
)
from ..services import SolapasService


def buscar_ciudadanos_rapido(q):
    """
    Búsqueda rápida para el header del backoffice.
    - Input numérico: busca por DNI exacto.
    - Input texto (≥3 chars): busca por nombre o apellido (icontains).
    Retorna máximo 10 ciudadanos activos con datos para el dropdown.
    """
    q = q.strip()
    if not q:
        return []

    qs = Ciudadano.objects.filter(activo=True)

    if q.isdigit():
        qs = qs.filter(dni=q)
    elif len(q) >= 3:
        qs = qs.filter(Q(nombre__icontains=q) | Q(apellido__icontains=q))
    else:
        return []

    from datetime import date as _date
    hoy = _date.today()
    resultados = []
    for c in qs.order_by('apellido', 'nombre')[:10]:
        edad = None
        if c.fecha_nacimiento:
            edad = hoy.year - c.fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (c.fecha_nacimiento.month, c.fecha_nacimiento.day)
            )
        resultados.append({
            'id': c.pk,
            'nombre': c.nombre,
            'apellido': c.apellido,
            'dni': c.dni,
            'edad': edad,
            'foto_url': c.foto.url if c.foto else None,
        })
    return resultados


def get_ciudadanos_queryset(search=""):
    queryset = Ciudadano.objects.filter(activo=True)
    if search:
        queryset = queryset.filter(
            Q(dni__icontains=search)
            | Q(nombre__icontains=search)
            | Q(apellido__icontains=search)
        )
    return queryset.order_by("apellido", "nombre")


def get_ciudadanos_dashboard_metrics():
    total_seguimientos = SeguimientoContacto.objects.count()
    seguimientos_adecuados = SeguimientoContacto.objects.filter(
        adherencia="ADECUADA"
    ).count()
    tasa_adherencia = round(
        (seguimientos_adecuados / total_seguimientos * 100)
        if total_seguimientos > 0
        else 0
    )

    return {
        "total_ciudadanos": Ciudadano.objects.filter(activo=True).count(),
        "legajos_activos": LegajoAtencion.objects.filter(
            estado__in=["ABIERTO", "EN_SEGUIMIENTO"]
        ).count(),
        "alertas_criticas": EventoCritico.objects.count(),
        "seguimientos_hoy": SeguimientoContacto.objects.filter(
            creado__date=date.today()
        ).count(),
        "tasa_adherencia": tasa_adherencia,
        "casos_alto_riesgo": LegajoAtencion.objects.filter(
            nivel_riesgo="ALTO"
        ).count(),
    }


def build_ciudadano_detail_context(ciudadano, user=None):
    import datetime
    from django.utils import timezone

    puede_ver_sensible = (
        user is not None
        and (user.is_superuser or user.groups.filter(name='ciudadanoSensible').exists())
    )

    # Generar alertas on-the-fly antes de consultar (best-effort)
    try:
        from ..services.alertas import AlertasService
        AlertasService.generar_alertas_ciudadano(ciudadano.pk)
    except Exception:
        pass

    context = {
        'puede_ver_sensible': puede_ver_sensible,
        'legajos': ciudadano.legajos.select_related('dispositivo', 'responsable').order_by('-fecha_admision'),
        'solapas': SolapasService.obtener_solapas_ciudadano(ciudadano),
        'programas_activos': SolapasService.obtener_programas_activos(ciudadano),
    }

    # --- Turnos ---
    try:
        from portal.models import TurnoCiudadano
        context['turnos_ciudadano'] = (
            ciudadano.turnos
            .select_related('configuracion', 'recurso')
            .order_by('-fecha', '-hora_inicio')[:20]
        )
    except Exception:
        context['turnos_ciudadano'] = []

    # --- Instituciones vinculadas (vía legajos) ---
    from core.models import Institucion
    institucion_ids = (
        ciudadano.legajos
        .exclude(dispositivo=None)
        .values_list('dispositivo_id', flat=True)
        .distinct()
    )
    context['instituciones_ciudadano'] = Institucion.objects.filter(pk__in=institucion_ids)

    # --- Conversaciones ---
    try:
        from conversaciones.models import Conversacion
        context['conversaciones_ciudadano'] = (
            Conversacion.objects
            .filter(dni_ciudadano=ciudadano.dni)
            .order_by('-fecha_inicio')[:20]
        )
    except Exception:
        context['conversaciones_ciudadano'] = []

    # --- Derivaciones ---
    context['derivaciones_ciudadano'] = (
        ciudadano.derivaciones_programas
        .select_related('programa_origen', 'programa_destino', 'derivado_por')
        .order_by('-creado')[:20]
    )

    # --- Alertas ---
    context['alertas_ciudadano'] = (
        ciudadano.alertas
        .filter(activa=True)
        .order_by('prioridad', '-creado')
    )

    # --- Línea de tiempo ---
    from ..models_programas import InscripcionPrograma
    linea = []

    for ins in InscripcionPrograma.objects.filter(ciudadano=ciudadano).select_related('programa').order_by('-fecha_inscripcion')[:20]:
        linea.append({
            'fecha': ins.fecha_inscripcion,
            'icono': 'user-plus',
            'color_hex': ins.programa.color or '#3B82F6',
            'titulo': f'Inscripción a {ins.programa.nombre}',
            'descripcion': ins.get_estado_display(),
        })

    for legajo in ciudadano.legajos.select_related('dispositivo').order_by('-fecha_admision')[:10]:
        linea.append({
            'fecha': legajo.fecha_admision,
            'icono': 'folder-open',
            'color_hex': '#6366F1',
            'titulo': f'Legajo {legajo.codigo}',
            'descripcion': legajo.dispositivo.nombre if legajo.dispositivo else '',
        })

    for deriv in ciudadano.derivaciones_programas.select_related('programa_destino').order_by('-creado')[:10]:
        linea.append({
            'fecha': deriv.creado.date() if hasattr(deriv.creado, 'date') else deriv.creado,
            'icono': 'share-alt',
            'color_hex': '#F97316',
            'titulo': f'Derivación a {deriv.programa_destino.nombre}',
            'descripcion': deriv.get_estado_display(),
        })

    linea.sort(key=lambda x: x['fecha'], reverse=True)
    context['linea_tiempo'] = linea[:50]

    caso_nachec = (
        CasoNachec.objects.filter(ciudadano_titular=ciudadano)
        .exclude(estado__in=["CERRADO", "RECHAZADO", "SUSPENDIDO"])
        .select_related("territorial", "coordinador", "operador_admision")
        .order_by("-creado")
        .first()
    )
    if not caso_nachec:
        return context

    context["caso_nachec"] = caso_nachec
    context["relevamiento"] = RelevamientoNachec.objects.filter(
        caso=caso_nachec
    ).order_by("-creado").first()
    context["evaluacion"] = EvaluacionVulnerabilidad.objects.filter(
        caso=caso_nachec
    ).first()
    context["plan_vigente"] = PlanIntervencionNachec.objects.filter(
        caso=caso_nachec,
        vigente=True,
    ).first()
    context["prestaciones"] = PrestacionNachec.objects.filter(
        caso=caso_nachec
    ).select_related("responsable").order_by("-creado")[:10]
    context["historial_estados"] = HistorialEstadoCaso.objects.filter(
        caso=caso_nachec
    ).select_related("usuario").order_by("-timestamp")[:10]
    return context
