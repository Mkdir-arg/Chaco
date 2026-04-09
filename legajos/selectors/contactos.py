from datetime import datetime

from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.shortcuts import get_object_or_404

from ..models import (
    Adjunto,
    Ciudadano,
    Derivacion,
    EventoCritico,
    LegajoAtencion,
    PlanIntervencion,
    SeguimientoContacto,
)

try:
    from ..models_contactos import VinculoFamiliar
except ImportError:  # pragma: no cover - compatibilidad legacy
    VinculoFamiliar = None


def get_legajo_contactos_context(legajo_id):
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    return {
        'legajo': legajo,
        'ciudadano': legajo.ciudadano,
    }


def _format_legajo_codigo(legajo):
    return f"{str(legajo.codigo)[:12]}..." if legajo.codigo else str(legajo.id)


def _serialize_adjunto(archivo, *, legajo=None, origen='ciudadano'):
    payload = {
        'id': archivo.id,
        'nombre': archivo.archivo.name.split('/')[-1],
        'etiqueta': archivo.etiqueta,
        'url': archivo.archivo.url,
        'tamano': archivo.archivo.size,
        'fecha_subida': archivo.creado.isoformat(),
        'tipo_origen': origen,
    }
    if legajo is None:
        payload.update({'legajo_id': '-', 'legajo_codigo': 'Ciudadano'})
    else:
        payload.update(
            {
                'legajo_id': str(legajo.id),
                'legajo_codigo': _format_legajo_codigo(legajo),
            }
        )
    return payload


def build_ciudadano_actividades_payload(ciudadano_id):
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
    legajos = LegajoAtencion.objects.filter(ciudadano=ciudadano).select_related(
        'dispositivo', 'responsable'
    )
    actividades = []

    for legajo in legajos:
        if legajo.fecha_apertura:
            actividades.append(
                {
                    'fecha_hora': legajo.fecha_apertura.isoformat(),
                    'tipo': 'APERTURA',
                    'descripcion': (
                        f'Acompañamiento abierto en '
                        f'{legajo.dispositivo.nombre if legajo.dispositivo else "Dispositivo no especificado"}'
                    ),
                    'usuario_nombre': legajo.responsable.get_full_name() if legajo.responsable else 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': _format_legajo_codigo(legajo),
                }
            )

        if legajo.fecha_cierre:
            actividades.append(
                {
                    'fecha_hora': legajo.fecha_cierre.isoformat(),
                    'tipo': 'CIERRE',
                    'descripcion': 'Acompañamiento cerrado',
                    'usuario_nombre': 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': _format_legajo_codigo(legajo),
                }
            )

        seguimientos = SeguimientoContacto.objects.filter(legajo=legajo).select_related(
            'profesional__usuario'
        )
        for seguimiento in seguimientos:
            actividades.append(
                {
                    'fecha_hora': seguimiento.creado.isoformat(),
                    'tipo': 'SEGUIMIENTO',
                    'descripcion': (
                        f'{seguimiento.get_tipo_display()}: '
                        f'{seguimiento.descripcion[:100] if seguimiento.descripcion else "Sin descripción"}'
                    ),
                    'usuario_nombre': (
                        seguimiento.profesional.usuario.get_full_name()
                        if seguimiento.profesional and seguimiento.profesional.usuario
                        else 'Sistema'
                    ),
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': _format_legajo_codigo(legajo),
                }
            )

        evaluacion = getattr(legajo, 'evaluacion', None)
        if evaluacion:
            actividades.append(
                {
                    'fecha_hora': evaluacion.creado.isoformat(),
                    'tipo': 'EVALUACION',
                    'descripcion': (
                        'Evaluación inicial realizada - '
                        f'Riesgo: {legajo.get_nivel_riesgo_display() if legajo.nivel_riesgo else "No especificado"}'
                    ),
                    'usuario_nombre': 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': _format_legajo_codigo(legajo),
                }
            )

        planes = PlanIntervencion.objects.filter(legajo=legajo).select_related('profesional__usuario')
        for plan in planes:
            actividades.append(
                {
                    'fecha_hora': plan.creado.isoformat(),
                    'tipo': 'PLAN',
                    'descripcion': (
                        'Plan de intervención creado - '
                        f'Actividades: {len(plan.actividades or [])}'
                    ),
                    'usuario_nombre': (
                        plan.profesional.usuario.get_full_name()
                        if plan.profesional and plan.profesional.usuario
                        else 'Sistema'
                    ),
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': _format_legajo_codigo(legajo),
                }
            )

        derivaciones = Derivacion.objects.filter(legajo=legajo).select_related('destino')
        for derivacion in derivaciones:
            actividades.append(
                {
                    'fecha_hora': derivacion.creado.isoformat(),
                    'tipo': 'DERIVACION',
                    'descripcion': (
                        f'Derivación a '
                        f'{derivacion.destino.nombre if derivacion.destino else "destino no especificado"}'
                        f' - Estado: {derivacion.get_estado_display()}'
                    ),
                    'usuario_nombre': 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': _format_legajo_codigo(legajo),
                }
            )

        eventos = EventoCritico.objects.filter(legajo=legajo)
        for evento in eventos:
            actividades.append(
                {
                    'fecha_hora': evento.creado.isoformat(),
                    'tipo': 'EVENTO',
                    'descripcion': (
                        f'Evento crítico: {evento.get_tipo_display()} - '
                        f'{evento.detalle[:100] if evento.detalle else ""}'
                    ),
                    'usuario_nombre': 'Sistema',
                    'legajo_id': str(legajo.id),
                    'legajo_codigo': _format_legajo_codigo(legajo),
                }
            )

    if VinculoFamiliar:
        for vinculo in VinculoFamiliar.objects.filter(ciudadano_principal=ciudadano):
            actividades.append(
                {
                    'fecha_hora': (
                        vinculo.creado.isoformat()
                        if hasattr(vinculo, 'creado')
                        else datetime.now().isoformat()
                    ),
                    'tipo': 'VINCULO',
                    'descripcion': (
                        'Vínculo agregado: '
                        f'{vinculo.get_tipo_vinculo_display() if hasattr(vinculo, "get_tipo_vinculo_display") else vinculo.tipo_vinculo}'
                    ),
                    'usuario_nombre': 'Sistema',
                    'legajo_id': '-',
                    'legajo_codigo': 'General',
                }
            )

    actividades.sort(key=lambda item: item['fecha_hora'] or '', reverse=True)
    return {
        'results': actividades[:50],
        'count': len(actividades),
    }


def build_ciudadano_archivos_payload(ciudadano_id):
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
    legajos = list(LegajoAtencion.objects.filter(ciudadano=ciudadano))
    ciudadano_content_type = ContentType.objects.get_for_model(Ciudadano)
    legajo_content_type = ContentType.objects.get_for_model(LegajoAtencion)

    archivos = Adjunto.objects.filter(
        Q(content_type=ciudadano_content_type, object_id=ciudadano.id)
        | Q(content_type=legajo_content_type, object_id__in=[legajo.id for legajo in legajos])
    ).order_by('-creado')

    legajos_por_id = {str(legajo.id): legajo for legajo in legajos}
    archivos_data = []
    for archivo in archivos:
        if archivo.content_type.model == 'ciudadano':
            archivos_data.append(_serialize_adjunto(archivo))
            continue
        legajo = legajos_por_id.get(str(archivo.object_id))
        if legajo:
            archivos_data.append(_serialize_adjunto(archivo, legajo=legajo, origen='legajo'))

    return {
        'results': archivos_data,
        'count': len(archivos_data),
    }


def build_legajo_archivos_payload(legajo_id):
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    content_type = ContentType.objects.get_for_model(LegajoAtencion)
    archivos = Adjunto.objects.filter(content_type=content_type, object_id=legajo.id).order_by('-creado')
    return {
        'success': True,
        'archivos': [
            {
                'id': archivo.id,
                'nombre': archivo.archivo.name.split('/')[-1],
                'etiqueta': archivo.etiqueta,
                'url': archivo.archivo.url,
                'fecha': archivo.creado.strftime('%d/%m/%Y %H:%M'),
            }
            for archivo in archivos
        ],
    }


def build_legajo_evolucion_payload(legajo_id):
    legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
    total_seguimientos = SeguimientoContacto.objects.filter(legajo=legajo).count()
    seguimientos_con_adherencia = SeguimientoContacto.objects.filter(
        legajo=legajo, adherencia__isnull=False
    )

    adherencia_promedio = None
    if seguimientos_con_adherencia.exists():
        adherencia_map = {'ADECUADA': 100, 'PARCIAL': 50, 'NULA': 0}
        total = sum(adherencia_map.get(seg.adherencia, 0) for seg in seguimientos_con_adherencia)
        adherencia_promedio = round(total / seguimientos_con_adherencia.count())

    plan_vigente = PlanIntervencion.objects.filter(legajo=legajo, vigente=True).first()
    objetivos_totales = len(plan_vigente.actividades or []) if plan_vigente else 0
    objetivos_cumplidos = (
        sum(1 for actividad in plan_vigente.actividades or [] if actividad.get('completada'))
        if plan_vigente
        else 0
    )

    hitos = [
        {
            'tipo': 'APERTURA',
            'titulo': 'Apertura de Acompañamiento',
            'fecha': legajo.fecha_apertura.isoformat(),
        }
    ]
    evaluacion = getattr(legajo, 'evaluacion', None)
    if evaluacion:
        hitos.append(
            {
                'tipo': 'EVALUACION',
                'titulo': 'Evaluación Inicial',
                'fecha': evaluacion.creado.isoformat(),
            }
        )
    if plan_vigente:
        hitos.append(
            {
                'tipo': 'PLAN',
                'titulo': 'Plan de Intervención Activo',
                'fecha': plan_vigente.creado.isoformat(),
            }
        )
    ultimo_seguimiento = SeguimientoContacto.objects.filter(legajo=legajo).order_by('-creado').first()
    if ultimo_seguimiento:
        hitos.append(
            {
                'tipo': 'SEGUIMIENTO',
                'titulo': f'Último Seguimiento - {ultimo_seguimiento.get_tipo_display()}',
                'fecha': ultimo_seguimiento.creado.isoformat(),
            }
        )
    derivacion_reciente = Derivacion.objects.filter(legajo=legajo).order_by('-creado').first()
    if derivacion_reciente:
        hitos.append(
            {
                'tipo': 'DERIVACION',
                'titulo': f'Derivación a {derivacion_reciente.destino.nombre}',
                'fecha': derivacion_reciente.creado.isoformat(),
            }
        )
    evento_reciente = EventoCritico.objects.filter(legajo=legajo).order_by('-creado').first()
    if evento_reciente:
        hitos.append(
            {
                'tipo': 'EVENTO',
                'titulo': f'Evento: {evento_reciente.get_tipo_display()}',
                'fecha': evento_reciente.creado.isoformat(),
            }
        )
    if legajo.fecha_cierre:
        hitos.append(
            {
                'tipo': 'CIERRE',
                'titulo': 'Cierre de Acompañamiento',
                'fecha': legajo.fecha_cierre.isoformat(),
            }
        )

    hitos.sort(key=lambda item: item['fecha'])
    return {
        'total_seguimientos': total_seguimientos,
        'adherencia_promedio': adherencia_promedio,
        'objetivos_totales': objetivos_totales,
        'objetivos_cumplidos': objetivos_cumplidos,
        'hitos': hitos,
    }


def build_ciudadano_timeline_payload(ciudadano_id):
    ciudadano = get_object_or_404(Ciudadano, id=ciudadano_id)
    legajos = LegajoAtencion.objects.filter(ciudadano=ciudadano).select_related('dispositivo', 'responsable')
    eventos = []

    for legajo in legajos:
        eventos.append(
            {
                'fecha': legajo.fecha_apertura.isoformat(),
                'tipo': 'APERTURA',
                'titulo': 'Apertura de Acompañamiento',
                'descripcion': (
                    f'Acompañamiento iniciado en '
                    f'{legajo.dispositivo.nombre if legajo.dispositivo else "dispositivo no especificado"}'
                ),
                'legajo_id': str(legajo.id),
            }
        )

        evaluacion = getattr(legajo, 'evaluacion', None)
        if evaluacion:
            eventos.append(
                {
                    'fecha': evaluacion.creado.isoformat(),
                    'tipo': 'EVALUACION',
                    'titulo': 'Evaluación Inicial',
                    'descripcion': (
                        f'Evaluación realizada - Nivel de riesgo: {legajo.get_nivel_riesgo_display()}'
                    ),
                    'legajo_id': str(legajo.id),
                }
            )

        for plan in PlanIntervencion.objects.filter(legajo=legajo, vigente=True):
            eventos.append(
                {
                    'fecha': plan.creado.isoformat(),
                    'tipo': 'PLAN',
                    'titulo': 'Plan de Intervención',
                    'descripcion': 'Plan de intervención creado y activado',
                    'legajo_id': str(legajo.id),
                }
            )

        for seguimiento in SeguimientoContacto.objects.filter(legajo=legajo).order_by('-creado')[:3]:
            eventos.append(
                {
                    'fecha': seguimiento.creado.isoformat(),
                    'tipo': 'SEGUIMIENTO',
                    'titulo': f'Seguimiento - {seguimiento.get_tipo_display()}',
                    'descripcion': seguimiento.descripcion[:150] if seguimiento.descripcion else 'Sin descripción',
                    'legajo_id': str(legajo.id),
                }
            )

        for derivacion in Derivacion.objects.filter(legajo=legajo).select_related('destino'):
            eventos.append(
                {
                    'fecha': derivacion.creado.isoformat(),
                    'tipo': 'DERIVACION',
                    'titulo': 'Derivación',
                    'descripcion': (
                        f'Derivado a '
                        f'{derivacion.destino.nombre if derivacion.destino else "destino no especificado"}'
                        f' - {derivacion.get_estado_display()}'
                    ),
                    'legajo_id': str(legajo.id),
                }
            )

        for evento in EventoCritico.objects.filter(legajo=legajo):
            eventos.append(
                {
                    'fecha': evento.creado.isoformat(),
                    'tipo': 'EVENTO',
                    'titulo': f'Evento Crítico - {evento.get_tipo_display()}',
                    'descripcion': evento.detalle[:150] if evento.detalle else '',
                    'legajo_id': str(legajo.id),
                }
            )

        if legajo.fecha_cierre:
            eventos.append(
                {
                    'fecha': legajo.fecha_cierre.isoformat(),
                    'tipo': 'CIERRE',
                    'titulo': 'Cierre de Acompañamiento',
                    'descripcion': f'Acompañamiento cerrado - Estado: {legajo.get_estado_display()}',
                    'legajo_id': str(legajo.id),
                }
            )

    if VinculoFamiliar:
        for vinculo in VinculoFamiliar.objects.filter(ciudadano_principal=ciudadano):
            eventos.append(
                {
                    'fecha': (
                        vinculo.creado.isoformat()
                        if hasattr(vinculo, 'creado')
                        else datetime.now().isoformat()
                    ),
                    'tipo': 'VINCULO',
                    'titulo': 'Vínculo Familiar',
                    'descripcion': (
                        'Vínculo agregado: '
                        f'{vinculo.get_tipo_vinculo_display() if hasattr(vinculo, "get_tipo_vinculo_display") else vinculo.tipo_vinculo}'
                    ),
                    'legajo_id': None,
                }
            )

    try:
        from ..models import AlertaCiudadano

        for alerta in AlertaCiudadano.objects.filter(
            ciudadano=ciudadano,
            prioridad__in=['CRITICA', 'ALTA'],
        ).order_by('-creado')[:5]:
            eventos.append(
                {
                    'fecha': alerta.creado.isoformat(),
                    'tipo': 'ALERTA',
                    'titulo': f'Alerta - {alerta.get_tipo_display()}',
                    'descripcion': alerta.mensaje,
                    'legajo_id': str(alerta.legajo.id) if alerta.legajo else None,
                }
            )
    except Exception:
        pass

    eventos.sort(key=lambda item: item['fecha'], reverse=True)
    return {
        'eventos': eventos[:30],
        'count': len(eventos),
    }
