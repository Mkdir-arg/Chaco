from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Max
from django.utils import timezone

from ..models_institucional import (
    CasoInstitucional,
    DerivacionCiudadano,
    DerivacionInstitucional,
    EstadoCaso,
    EstadoDerivacion,
    EstadoDerivacionCiudadano,
    EstadoGlobal,
    EstadoPrograma,
)


class DerivacionService:
    """Servicio para gestión de derivaciones institucionales."""

    @staticmethod
    @transaction.atomic
    def aceptar_derivacion(derivacion_id, usuario, responsable_caso=None):
        derivacion = DerivacionInstitucional.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacion.PENDIENTE:
            raise ValidationError(
                f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})"
            )

        if hasattr(derivacion.institucion, "legajo_institucional"):
            estado_global = derivacion.institucion.legajo_institucional.estado_global
            if estado_global == EstadoGlobal.CERRADO:
                raise ValidationError(
                    "La institución está cerrada globalmente y no puede aceptar derivaciones"
                )

        if derivacion.institucion_programa.estado_programa != EstadoPrograma.ACTIVO:
            raise ValidationError(
                f"El programa está en estado "
                f"{derivacion.institucion_programa.get_estado_programa_display()} "
                "y no puede aceptar derivaciones"
            )

        if not derivacion.institucion_programa.activo:
            raise ValidationError("El programa no está activo en esta institución")

        if derivacion.institucion_programa.controlar_cupo:
            casos_activos = CasoInstitucional.objects.filter(
                institucion_programa=derivacion.institucion_programa,
                estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO],
            ).count()

            cupo_maximo = derivacion.institucion_programa.cupo_maximo

            if (
                casos_activos >= cupo_maximo
                and not derivacion.institucion_programa.permite_sobrecupo
            ):
                raise ValidationError(
                    f"Cupo lleno ({casos_activos}/{cupo_maximo}). "
                    "No se permite sobrecupo en este programa."
                )

        caso_existente = CasoInstitucional.objects.filter(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
            estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO],
        ).first()

        if caso_existente:
            derivacion.estado = EstadoDerivacion.ACEPTADA_UNIFICADA
            derivacion.caso_creado = caso_existente
            derivacion.respondido_por = usuario
            derivacion.fecha_respuesta = timezone.now()
            derivacion.respuesta = f"Unificada con caso existente {caso_existente.codigo}"
            derivacion.save()
            return caso_existente, False

        ultima_version = CasoInstitucional.objects.filter(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
        ).aggregate(Max("version"))["version__max"] or 0

        caso = CasoInstitucional.objects.create(
            ciudadano=derivacion.ciudadano,
            institucion_programa=derivacion.institucion_programa,
            version=ultima_version + 1,
            estado=EstadoCaso.ACTIVO,
            responsable=responsable_caso or usuario,
        )

        derivacion.estado = EstadoDerivacion.ACEPTADA
        derivacion.caso_creado = caso
        derivacion.respondido_por = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.respuesta = f"Caso creado: {caso.codigo}"
        derivacion.save()

        return caso, True

    @staticmethod
    @transaction.atomic
    def rechazar_derivacion(derivacion_id, usuario, motivo_rechazo):
        derivacion = DerivacionInstitucional.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacion.PENDIENTE:
            raise ValidationError(
                f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})"
            )

        derivacion.estado = EstadoDerivacion.RECHAZADA
        derivacion.respuesta = motivo_rechazo
        derivacion.respondido_por = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.save()


class DerivacionCiudadanoService:
    """Servicio para gestión de derivaciones usando el modelo unificado DerivacionCiudadano."""

    @staticmethod
    @transaction.atomic
    def aceptar_derivacion(derivacion_id, usuario, responsable_caso=None):
        derivacion = DerivacionCiudadano.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacionCiudadano.PENDIENTE:
            raise ValidationError(
                f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})"
            )

        if derivacion.institucion_programa:
            ip = derivacion.institucion_programa
            if hasattr(ip.institucion, 'legajo_institucional'):
                estado_global = ip.institucion.legajo_institucional.estado_global
                if estado_global == EstadoGlobal.CERRADO:
                    raise ValidationError(
                        'La institución está cerrada globalmente y no puede aceptar derivaciones'
                    )

            if ip.estado_programa != EstadoPrograma.ACTIVO:
                raise ValidationError(
                    f'El programa está en estado {ip.get_estado_programa_display()} '
                    'y no puede aceptar derivaciones'
                )

            if not ip.activo:
                raise ValidationError('El programa no está activo en esta institución')

            if ip.controlar_cupo:
                casos_activos = CasoInstitucional.objects.filter(
                    institucion_programa=ip,
                    estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO],
                ).count()
                cupo_maximo = ip.cupo_maximo
                if casos_activos >= cupo_maximo and not ip.permite_sobrecupo:
                    raise ValidationError(
                        f'Cupo lleno ({casos_activos}/{cupo_maximo}). '
                        'No se permite sobrecupo en este programa.'
                    )

            caso_existente = CasoInstitucional.objects.filter(
                ciudadano=derivacion.ciudadano,
                institucion_programa=ip,
                estado__in=[EstadoCaso.ACTIVO, EstadoCaso.EN_SEGUIMIENTO],
            ).first()

            if caso_existente:
                derivacion.estado = EstadoDerivacionCiudadano.ACEPTADA
                derivacion.caso_creado = caso_existente
                derivacion.quien_responde = usuario
                derivacion.fecha_respuesta = timezone.now()
                derivacion.respuesta = f'Unificada con caso existente {caso_existente.codigo}'
                derivacion.save()
                return caso_existente, False

            ultima_version = CasoInstitucional.objects.filter(
                ciudadano=derivacion.ciudadano,
                institucion_programa=ip,
            ).aggregate(Max('version'))['version__max'] or 0

            caso = CasoInstitucional.objects.create(
                ciudadano=derivacion.ciudadano,
                institucion_programa=ip,
                version=ultima_version + 1,
                estado=EstadoCaso.ACTIVO,
                responsable=responsable_caso or usuario,
            )

            derivacion.estado = EstadoDerivacionCiudadano.ACEPTADA
            derivacion.caso_creado = caso
            derivacion.quien_responde = usuario
            derivacion.fecha_respuesta = timezone.now()
            derivacion.respuesta = f'Caso creado: {caso.codigo}'
            derivacion.save()

            return caso, True

        raise ValidationError('La derivación no tiene destino válido (institucion_programa requerido)')

    @staticmethod
    @transaction.atomic
    def aceptar_derivacion_programa(derivacion_id, usuario):
        """
        Acepta una DerivacionCiudadano con destino a un programa, creando la InscripcionPrograma.
        Usado por el flujo ciudadano→programa (US-012). Distinto de aceptar_derivacion que crea CasoInstitucional.
        """
        from ..models_programas import InscripcionPrograma

        derivacion = DerivacionCiudadano.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacionCiudadano.PENDIENTE:
            raise ValidationError(
                f'La derivación ya fue procesada (estado: {derivacion.get_estado_display()})'
            )

        if not derivacion.institucion_programa:
            raise ValidationError('La derivación no tiene programa destino')

        ip = derivacion.institucion_programa

        if ip.estado_programa != EstadoPrograma.ACTIVO:
            raise ValidationError(
                f'El programa está en estado {ip.get_estado_programa_display()} '
                'y no puede aceptar derivaciones'
            )

        if not ip.activo:
            raise ValidationError('El programa no está activo en esta institución')

        programa = ip.programa

        # Verificar si ya existe inscripción activa
        inscripcion_existente = InscripcionPrograma.objects.filter(
            ciudadano=derivacion.ciudadano,
            programa=programa,
            estado__in=['ACTIVO', 'EN_SEGUIMIENTO'],
        ).first()

        if inscripcion_existente:
            derivacion.estado = EstadoDerivacionCiudadano.ACEPTADA
            derivacion.quien_responde = usuario
            derivacion.fecha_respuesta = timezone.now()
            derivacion.respuesta = f'Unificada con inscripción existente {inscripcion_existente.codigo}'
            derivacion.inscripcion_creada = inscripcion_existente
            derivacion.save()
            return inscripcion_existente, False

        # Manejar inscripción cerrada previa (unique_together) reactivándola
        inscripcion_cerrada = InscripcionPrograma.objects.filter(
            ciudadano=derivacion.ciudadano,
            programa=programa,
        ).first()

        if inscripcion_cerrada:
            inscripcion_cerrada.estado = 'PENDIENTE'
            inscripcion_cerrada.via_ingreso = (
                'DERIVACION_INTERNA' if derivacion.programa_origen else 'DERIVACION_EXTERNA'
            )
            inscripcion_cerrada.responsable = usuario
            inscripcion_cerrada.notas = (
                f"Reingreso. Motivo: {derivacion.motivo}"
            )
            inscripcion_cerrada.save()
            inscripcion = inscripcion_cerrada
        else:
            inscripcion = InscripcionPrograma.objects.create(
                ciudadano=derivacion.ciudadano,
                programa=programa,
                via_ingreso=(
                    'DERIVACION_INTERNA' if derivacion.programa_origen else 'DERIVACION_EXTERNA'
                ),
                estado='PENDIENTE',
                responsable=usuario,
                notas=f"Derivado por: {derivacion.derivado_por}\nMotivo: {derivacion.motivo}",
            )

        derivacion.estado = EstadoDerivacionCiudadano.ACEPTADA
        derivacion.quien_responde = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.respuesta = f'Inscripción creada: {inscripcion.codigo}'
        derivacion.inscripcion_creada = inscripcion
        derivacion.save()

        return inscripcion, True

    @staticmethod
    @transaction.atomic
    def rechazar_derivacion_programa(derivacion_id, usuario, motivo_rechazo):
        """Rechaza una DerivacionCiudadano con destino a un programa."""
        derivacion = DerivacionCiudadano.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacionCiudadano.PENDIENTE:
            raise ValidationError(
                f'La derivación ya fue procesada (estado: {derivacion.get_estado_display()})'
            )

        derivacion.estado = EstadoDerivacionCiudadano.RECHAZADA
        derivacion.respuesta = motivo_rechazo
        derivacion.quien_responde = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.save()

    @staticmethod
    @transaction.atomic
    def rechazar_derivacion(derivacion_id, usuario, motivo_rechazo):
        derivacion = DerivacionCiudadano.objects.select_for_update().get(id=derivacion_id)

        if derivacion.estado != EstadoDerivacionCiudadano.PENDIENTE:
            raise ValidationError(
                f"La derivación ya fue procesada (estado: {derivacion.get_estado_display()})"
            )

        derivacion.estado = EstadoDerivacionCiudadano.RECHAZADA
        derivacion.respuesta = motivo_rechazo
        derivacion.quien_responde = usuario
        derivacion.fecha_respuesta = timezone.now()
        derivacion.save()


class CasoService:
    """Servicio para gestión de casos institucionales."""

    @staticmethod
    @transaction.atomic
    def cambiar_estado_caso(caso_id, nuevo_estado, usuario, observacion="", motivo_cierre=""):
        caso = CasoInstitucional.objects.select_for_update().get(id=caso_id)

        estado_anterior = caso.estado
        if estado_anterior == nuevo_estado:
            raise ValidationError("El caso ya está en ese estado")

        caso.estado = nuevo_estado

        if nuevo_estado in [EstadoCaso.CERRADO, EstadoCaso.EGRESADO]:
            caso.fecha_cierre = timezone.now().date()
            if motivo_cierre:
                prefijo = f"[CIERRE] {motivo_cierre}"
                caso.observaciones = f"{caso.observaciones}\n\n{prefijo}" if caso.observaciones else prefijo

        if observacion:
            caso.observaciones = f"{caso.observaciones}\n\n{observacion}" if caso.observaciones else observacion

        caso.save()
        return caso

    @staticmethod
    @transaction.atomic
    def reabrir_caso(caso_id, usuario, observacion=""):
        caso = CasoInstitucional.objects.select_for_update().get(id=caso_id)

        if caso.estado not in [EstadoCaso.CERRADO, EstadoCaso.EGRESADO]:
            raise ValidationError("Solo se pueden reabrir casos cerrados o egresados")

        caso.estado = EstadoCaso.ACTIVO
        caso.fecha_cierre = None

        if observacion:
            nota_reapertura = f"[REAPERTURA] {observacion}"
            caso.observaciones = f"{caso.observaciones}\n\n{nota_reapertura}" if caso.observaciones else nota_reapertura

        caso.save()
        return caso
