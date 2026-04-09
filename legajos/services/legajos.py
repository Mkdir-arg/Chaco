from django.core.exceptions import ValidationError

from ..models import AlertaEventoCritico, EvaluacionInicial, Profesional


class LegajoWorkflowService:
    @staticmethod
    def get_or_create_profesional(usuario):
        profesional, _ = Profesional.objects.get_or_create(
            usuario=usuario,
            defaults={'rol': 'Operador'},
        )
        return profesional

    @classmethod
    def get_or_create_evaluacion(cls, legajo):
        evaluacion, _ = EvaluacionInicial.objects.get_or_create(
            legajo=legajo,
            defaults={},
        )
        return evaluacion

    @staticmethod
    def save_evaluacion_from_form(form, legajo):
        evaluacion = form.save(commit=False)
        evaluacion.legajo = legajo
        evaluacion.tamizajes = form.build_tamizajes_payload()
        evaluacion.save()
        return evaluacion

    @classmethod
    def save_plan_from_form(cls, form, legajo, usuario):
        plan = form.save(commit=False)
        plan.legajo = legajo
        if not plan.profesional_id:
            plan.profesional = cls.get_or_create_profesional(usuario)
        plan.actividades = form.get_actividades_payload()
        plan.save()
        return plan

    @classmethod
    def save_seguimiento_from_form(cls, form, legajo, usuario):
        seguimiento = form.save(commit=False)
        seguimiento.legajo = legajo
        if not seguimiento.profesional_id:
            seguimiento.profesional = cls.get_or_create_profesional(usuario)
        seguimiento.save()
        return seguimiento

    @staticmethod
    def save_derivacion_from_form(form, legajo):
        derivacion = form.save(commit=False)
        derivacion.legajo = legajo
        derivacion.save()
        return derivacion

    @staticmethod
    def save_evento_from_form(form, legajo):
        evento = form.save(commit=False)
        evento.legajo = legajo
        evento.notificado_a = form.get_notificados_payload()
        evento.save()
        return evento

    @staticmethod
    def close_legajo(legajo, motivo_cierre, usuario):
        legajo.cerrar(motivo_cierre=motivo_cierre, usuario=usuario)
        return legajo

    @staticmethod
    def reopen_legajo(legajo, motivo_reapertura, usuario):
        legajo.reabrir(motivo_reapertura=motivo_reapertura, usuario=usuario)
        return legajo

    @staticmethod
    def close_alerta_evento(evento, usuario):
        if evento.legajo.responsable != usuario:
            raise ValidationError('No autorizado')

        alerta, _ = AlertaEventoCritico.objects.get_or_create(
            evento=evento,
            responsable=usuario,
        )
        return alerta

    @staticmethod
    def change_legajo_responsable(legajo, nuevo_responsable, actor):
        if not (actor.is_superuser or actor.groups.filter(name='Administrador').exists() or legajo.responsable == actor):
            raise ValidationError('No tiene permisos para cambiar el responsable')

        responsable_anterior = legajo.responsable
        legajo.responsable = nuevo_responsable
        nota_cambio = (
            f"Responsable cambiado de "
            f"{responsable_anterior.get_full_name() or responsable_anterior.username} "
            f"a {nuevo_responsable.get_full_name() or nuevo_responsable.username} "
            f"por {actor.get_full_name() or actor.username}"
        )
        if legajo.notas:
            legajo.notas += f"\n\n{nota_cambio}"
        else:
            legajo.notas = nota_cambio
        legajo.save()
        return legajo
