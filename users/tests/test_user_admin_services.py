from django.contrib.auth.models import Group, User
from django.test import TestCase

from core.models import Provincia
from users.forms import CustomUserChangeForm, UserCreationForm
from users.models import Profile
from users.services_admin import UsuariosAdminService


class UsuariosAdminServiceTests(TestCase):
    def setUp(self):
        self.group_admin = Group.objects.create(name="Administrador")
        self.group_view = Group.objects.create(name="Usuario Ver")
        self.provincia = Provincia.objects.create(nombre="San Luis")

    def test_create_user_from_form_persists_groups_profile_and_password(self):
        form = UserCreationForm(
            data={
                "username": "operador1",
                "email": "operador1@example.com",
                "password": "clave-segura-123",
                "groups[]": [str(self.group_admin.pk), str(self.group_view.pk)],
                "es_usuario_provincial": "on",
                "provincia": str(self.provincia.pk),
                "last_name": "Perez",
                "first_name": "Ana",
                "rol": "Coordinadora",
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

        user = UsuariosAdminService.create_user_from_form(form)

        self.assertEqual(user.username, "operador1")
        self.assertTrue(user.check_password("clave-segura-123"))
        self.assertCountEqual(
            list(user.groups.values_list("name", flat=True)),
            ["Administrador", "Usuario Ver"],
        )
        self.assertTrue(user.profile.es_usuario_provincial)
        self.assertEqual(user.profile.provincia, self.provincia)
        self.assertEqual(user.profile.rol, "Coordinadora")

    def test_update_user_from_form_keeps_existing_password_when_blank(self):
        user = User.objects.create_user(
            username="operador2",
            email="old@example.com",
            password="clave-original",
            first_name="Luis",
            last_name="Gomez",
        )
        user.groups.add(self.group_view)
        profile = Profile.objects.create(user=user)
        profile.es_usuario_provincial = True
        profile.provincia = self.provincia
        profile.rol = "Analista"
        profile.save()
        original_password_hash = user.password

        form = CustomUserChangeForm(
            data={
                "username": "operador2",
                "email": "new@example.com",
                "password": "",
                "groups": [str(self.group_admin.pk)],
                "provincia": "",
                "last_name": "Gomez",
                "first_name": "Luis",
                "rol": "Supervisor",
            },
            instance=user,
        )
        self.assertTrue(form.is_valid(), form.errors)

        updated_user = UsuariosAdminService.update_user_from_form(form)
        updated_user.refresh_from_db()

        self.assertEqual(updated_user.email, "new@example.com")
        self.assertEqual(updated_user.password, original_password_hash)
        self.assertTrue(updated_user.check_password("clave-original"))
        self.assertCountEqual(
            list(updated_user.groups.values_list("name", flat=True)),
            ["Administrador"],
        )
        self.assertFalse(updated_user.profile.es_usuario_provincial)
        self.assertIsNone(updated_user.profile.provincia)
        self.assertEqual(updated_user.profile.rol, "Supervisor")
