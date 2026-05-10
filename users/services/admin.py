from django.contrib.auth.models import User
from django.db import transaction

from ..models import Profile


class UsuariosAdminService:
    @staticmethod
    @transaction.atomic
    def create_user_from_form(form):
        user = User()
        UsuariosAdminService._apply_user_data(form, user)
        user.save()
        UsuariosAdminService._sync_related_data(user, form.cleaned_data)
        return user

    @staticmethod
    @transaction.atomic
    def update_user_from_form(form):
        user = form.instance
        UsuariosAdminService._apply_user_data(form, user)
        user.save()
        UsuariosAdminService._sync_related_data(user, form.cleaned_data)
        return user

    @staticmethod
    def _apply_user_data(form, user):
        cleaned_data = form.cleaned_data
        user.username = cleaned_data["username"]
        user.email = cleaned_data["email"]
        user.first_name = cleaned_data["first_name"]
        user.last_name = cleaned_data["last_name"]

        password = cleaned_data.get("password")
        if password:
            user.set_password(password)
        elif hasattr(form, "_original_password_hash"):
            user.password = form._original_password_hash

    @staticmethod
    def _sync_related_data(user, cleaned_data):
        user.groups.set(cleaned_data.get("groups", []))

        profile, _ = Profile.objects.get_or_create(user=user)
        profile.rol = cleaned_data.get("rol")
        profile.save()
