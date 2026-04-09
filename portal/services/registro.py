from django.contrib.auth.models import Group, User
from django.db import transaction


class PortalRegistroService:
    @staticmethod
    @transaction.atomic
    def create_pending_user(cleaned_data):
        user = User.objects.create_user(
            username=cleaned_data["username"],
            email=cleaned_data["email"],
            password=cleaned_data["password"],
            first_name=cleaned_data["first_name"],
            last_name=cleaned_data["last_name"],
            is_active=False,
        )
        grupo_institucion, _ = Group.objects.get_or_create(
            name="EncargadoInstitucion"
        )
        user.groups.add(grupo_institucion)
        return user

    @staticmethod
    @transaction.atomic
    def create_institucion_from_form(form, pending_user=None, authenticated_user=None):
        institucion = form.save(commit=False)
        institucion.estado_registro = "ENVIADO"
        institucion.save()

        if pending_user is not None:
            institucion.encargados.add(pending_user)
        elif authenticated_user and authenticated_user.is_authenticated:
            institucion.encargados.add(authenticated_user)

        return institucion

    @staticmethod
    def get_pending_user(pending_user_id):
        if not pending_user_id:
            return None
        return User.objects.filter(id=pending_user_id).first()
