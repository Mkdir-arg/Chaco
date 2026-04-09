from django.shortcuts import get_object_or_404

from ..models import Ciudadano, LegajoAtencion
from ..models_programas import InscripcionPrograma


class AdmisionSessionService:
    CIUDADANO_SESSION_KEY = "admision_ciudadano_id"
    LEGAJO_SESSION_KEY = "admision_legajo_id"
    INSCRIPCION_SESSION_KEY = "inscripcion_programa_id"

    @classmethod
    def set_ciudadano_id(cls, session, ciudadano_id):
        session[cls.CIUDADANO_SESSION_KEY] = ciudadano_id

    @classmethod
    def get_ciudadano_id(cls, session):
        return session.get(cls.CIUDADANO_SESSION_KEY)

    @classmethod
    def pop_ciudadano_id(cls, session):
        return session.pop(cls.CIUDADANO_SESSION_KEY, None)

    @classmethod
    def set_legajo_id(cls, session, legajo_id):
        session[cls.LEGAJO_SESSION_KEY] = str(legajo_id)

    @classmethod
    def get_legajo_id(cls, session):
        return session.get(cls.LEGAJO_SESSION_KEY)

    @classmethod
    def pop_legajo_id(cls, session):
        return session.pop(cls.LEGAJO_SESSION_KEY, None)

    @classmethod
    def link_inscripcion_programa_if_pending(cls, session, legajo):
        inscripcion_id = session.get(cls.INSCRIPCION_SESSION_KEY)
        if not inscripcion_id:
            return

        inscripcion = InscripcionPrograma.objects.filter(id=inscripcion_id).first()
        if inscripcion:
            inscripcion.legajo_id = legajo.id
            inscripcion.save(update_fields=["legajo_id"])
        session.pop(cls.INSCRIPCION_SESSION_KEY, None)

    @classmethod
    def create_legajo_from_form(cls, form, session, user):
        ciudadano_id = cls.get_ciudadano_id(session)
        form.instance.ciudadano_id = ciudadano_id
        if not form.instance.responsable:
            form.instance.responsable = user
        legajo = form.save()
        cls.link_inscripcion_programa_if_pending(session, legajo)
        cls.pop_ciudadano_id(session)
        cls.set_legajo_id(session, legajo.id)
        return legajo

    @classmethod
    def create_consentimiento_from_form(cls, form, session):
        legajo_id = cls.get_legajo_id(session)
        legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
        form.instance.ciudadano = legajo.ciudadano
        consentimiento = form.save()
        cls.pop_legajo_id(session)
        return legajo, consentimiento

    @classmethod
    def finalize_without_consent(cls, session):
        legajo_id = cls.get_legajo_id(session)
        legajo = get_object_or_404(LegajoAtencion, id=legajo_id)
        cls.pop_legajo_id(session)
        return legajo

    @classmethod
    def get_ciudadano_from_session(cls, session):
        ciudadano_id = cls.get_ciudadano_id(session)
        return get_object_or_404(Ciudadano, id=ciudadano_id)

    @classmethod
    def get_legajo_from_session(cls, session):
        legajo_id = cls.get_legajo_id(session)
        return get_object_or_404(LegajoAtencion, id=legajo_id)
