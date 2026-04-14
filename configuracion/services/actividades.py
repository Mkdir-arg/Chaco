from django.db import transaction
from django.utils import timezone

from legajos.models import (
    Derivacion,
    HistorialActividad,
    HistorialDerivacion,
    HistorialInscripto,
    HistorialStaff,
    InscriptoActividad,
    PersonalInstitucion,
    StaffActividad,
)
from legajos.services.actividades import InscripcionError, inscribir_ciudadano_a_actividad


class ConfiguracionWorkflowError(Exception):
    pass


class ConfiguracionInstitucionalService:
    @staticmethod
    @transaction.atomic
    def assign_staff_to_actividad(
        actividad,
        *,
        rol_en_actividad,
        activo,
        usuario,
        personal=None,
        personal_data=None,
    ):
        if personal_data is not None:
            personal = PersonalInstitucion(
                legajo_institucional=actividad.legajo_institucional,
                activo=True,
                **personal_data,
            )
            personal.full_clean()
            personal.save()
            usuario_creado = personal.crear_usuario()
        else:
            usuario_creado = None

        if personal is None:
            raise ConfiguracionWorkflowError(
                "Debe seleccionar un personal existente o crear uno nuevo."
            )

        if StaffActividad.objects.filter(
            actividad=actividad, personal=personal
        ).exists():
            raise ConfiguracionWorkflowError(
                f"El personal {personal.nombre} {personal.apellido} ya está asignado a esta actividad."
            )

        staff = StaffActividad.objects.create(
            actividad=actividad,
            personal=personal,
            rol_en_actividad=rol_en_actividad,
            activo=activo,
        )
        HistorialStaff.objects.create(
            staff=staff,
            accion=HistorialStaff.TipoAccion.ASIGNACION,
            usuario=usuario,
            descripcion=(
                f"{personal.nombre} {personal.apellido} "
                f"{'creado y asignado' if personal_data is not None else 'asignado'} como "
                f"{staff.rol_en_actividad}"
            ),
        )
        return staff, usuario_creado

    @staticmethod
    @transaction.atomic
    def update_inscripto_estado(inscripto, *, estado, observaciones, usuario):
        if estado == inscripto.estado:
            return False

        estado_anterior = inscripto.estado
        inscripto.estado = estado
        inscripto.observaciones = observaciones
        if estado in [InscriptoActividad.Estado.FINALIZADO, InscriptoActividad.Estado.ABANDONADO]:
            inscripto.fecha_finalizacion = timezone.now().date()
        else:
            inscripto.fecha_finalizacion = None
        inscripto.save()

        accion_map = {
            InscriptoActividad.Estado.FINALIZADO: HistorialInscripto.TipoAccion.FINALIZACION,
            InscriptoActividad.Estado.ABANDONADO: HistorialInscripto.TipoAccion.ABANDONO,
            InscriptoActividad.Estado.ACTIVO: HistorialInscripto.TipoAccion.ACTIVACION,
        }
        HistorialInscripto.objects.create(
            inscripto=inscripto,
            accion=accion_map.get(
                estado, HistorialInscripto.TipoAccion.INSCRIPCION
            ),
            usuario=usuario,
            descripcion=(
                f"Estado cambiado a {inscripto.get_estado_display()}. "
                f"{observaciones}"
            ).strip(),
            estado_anterior=estado_anterior,
        )
        return True

    @staticmethod
    @transaction.atomic
    def update_actividad(actividad, cleaned_data, usuario):
        cambios = []
        original = {
            "nombre": actividad.nombre,
            "descripcion": actividad.descripcion,
            "cupo_ciudadanos": actividad.cupo_ciudadanos,
            "fecha_inicio": actividad.fecha_inicio,
            "fecha_fin": actividad.fecha_fin,
            "estado": actividad.estado,
        }

        for field, value in cleaned_data.items():
            if getattr(actividad, field) != value:
                setattr(actividad, field, value)
                cambios.append(field)

        if not cambios:
            return []

        actividad.save()

        cambios_descripcion = []
        if original["nombre"] != actividad.nombre:
            cambios_descripcion.append(
                f"Nombre: '{original['nombre']}' -> '{actividad.nombre}'"
            )
        if original["cupo_ciudadanos"] != actividad.cupo_ciudadanos:
            cambios_descripcion.append(
                f"Cupo: {original['cupo_ciudadanos']} -> {actividad.cupo_ciudadanos}"
            )
        if original["estado"] != actividad.estado:
            cambios_descripcion.append(
                f"Estado: {original['estado']} -> {actividad.estado}"
            )
        if original["fecha_inicio"] != actividad.fecha_inicio:
            cambios_descripcion.append(
                f"Inicio: {original['fecha_inicio']} -> {actividad.fecha_inicio}"
            )
        if original["fecha_fin"] != actividad.fecha_fin:
            cambios_descripcion.append(
                f"Fin: {original['fecha_fin']} -> {actividad.fecha_fin}"
            )

        accion = HistorialActividad.TipoAccion.MODIFICACION
        if actividad.estado == "SUSPENDIDO":
            accion = HistorialActividad.TipoAccion.SUSPENSION
        elif actividad.estado == "FINALIZADO":
            accion = HistorialActividad.TipoAccion.FINALIZACION

        HistorialActividad.objects.create(
            actividad=actividad,
            accion=accion,
            usuario=usuario,
            descripcion=f"Actividad modificada: {'; '.join(cambios_descripcion)}",
            datos_anteriores=original,
        )
        return cambios_descripcion

    @staticmethod
    @transaction.atomic
    def update_staff(staff, *, rol_en_actividad, activo, usuario):
        cambios = []
        if staff.rol_en_actividad != rol_en_actividad:
            cambios.append(
                f"Rol: '{staff.rol_en_actividad}' -> '{rol_en_actividad}'"
            )
            staff.rol_en_actividad = rol_en_actividad

        if staff.activo != activo:
            cambios.append(
                "Estado: "
                f"{'Activo' if staff.activo else 'Inactivo'} -> "
                f"{'Activo' if activo else 'Inactivo'}"
            )
            staff.activo = activo

        if not cambios:
            return []

        staff.save()
        HistorialStaff.objects.create(
            staff=staff,
            accion=(
                HistorialStaff.TipoAccion.DESASIGNACION
                if not activo
                else HistorialStaff.TipoAccion.CAMBIO_ROL
            ),
            usuario=usuario,
            descripcion=f"Staff modificado: {'; '.join(cambios)}",
        )
        return cambios

    @staticmethod
    @transaction.atomic
    def deactivate_staff(staff, usuario):
        if not staff.activo:
            return False

        staff.activo = False
        staff.save(update_fields=["activo", "modificado"])
        HistorialStaff.objects.create(
            staff=staff,
            accion=HistorialStaff.TipoAccion.DESASIGNACION,
            usuario=usuario,
            descripcion=(
                f"{staff.personal.nombre} {staff.personal.apellido} "
                f"desasignado de {staff.actividad.nombre}"
            ),
        )
        return True

    @staticmethod
    @transaction.atomic
    def aceptar_derivacion(derivacion_id, usuario):
        derivacion = Derivacion.objects.select_for_update().select_related(
            "actividad_destino",
            "legajo__ciudadano",
        ).get(pk=derivacion_id)

        if derivacion.estado != Derivacion.Estado.PENDIENTE:
            raise ConfiguracionWorkflowError(
                "La derivación ya fue procesada por otro operador."
            )

        estado_anterior = derivacion.estado
        derivacion.estado = Derivacion.Estado.ACEPTADA
        derivacion.fecha_aceptacion = timezone.now().date()
        derivacion.save(update_fields=["estado", "fecha_aceptacion", "modificado"])

        try:
            inscripto = inscribir_ciudadano_a_actividad(
                actividad=derivacion.actividad_destino,
                ciudadano=derivacion.legajo.ciudadano,
                usuario=usuario,
                observaciones=f"Inscripto via derivación #{derivacion_id}",
            )
        except InscripcionError as exc:
            raise ConfiguracionWorkflowError(str(exc)) from exc

        HistorialDerivacion.objects.create(
            derivacion=derivacion,
            accion=HistorialDerivacion.TipoAccion.ACEPTACION,
            usuario=usuario,
            descripcion=f"Derivación aceptada por {usuario.username}",
            estado_anterior=estado_anterior,
        )
        return derivacion, inscripto

    @staticmethod
    @transaction.atomic
    def rechazar_derivacion(derivacion_id, usuario, motivo):
        derivacion = Derivacion.objects.select_for_update().select_related(
            "actividad_destino"
        ).get(pk=derivacion_id)

        if derivacion.estado != Derivacion.Estado.PENDIENTE:
            raise ConfiguracionWorkflowError(
                "La derivación ya fue procesada por otro operador."
            )

        estado_anterior = derivacion.estado
        derivacion.estado = Derivacion.Estado.RECHAZADA
        derivacion.respuesta = motivo or "Rechazada"
        derivacion.save(update_fields=["estado", "respuesta", "modificado"])

        HistorialDerivacion.objects.create(
            derivacion=derivacion,
            accion=HistorialDerivacion.TipoAccion.RECHAZO,
            usuario=usuario,
            descripcion=(
                f"Derivación rechazada por {usuario.username}: "
                f"{derivacion.respuesta}"
            ),
            estado_anterior=estado_anterior,
        )
        return derivacion
