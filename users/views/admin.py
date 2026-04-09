import logging

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.mixins import TimestampedSuccessUrlMixin
from ..forms import CustomUserChangeForm, UserCreationForm
from ..services import UsuariosService
from ..services.admin import UsuariosAdminService

logger = logging.getLogger(__name__)


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or self.request.user.groups.filter(
            name="Administrador"
        ).exists()


class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "user/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return UsuariosService.get_filtered_usuarios(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(UsuariosService.get_usuarios_list_context())
        return context


class UserCreateView(TimestampedSuccessUrlMixin, AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreationForm
    template_name = "user/user_form.html"
    success_url = reverse_lazy("users:usuarios")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_groups"] = Group.objects.all().order_by("name")
        return context

    def form_valid(self, form):
        try:
            self.object = UsuariosAdminService.create_user_from_form(form)
        except Exception as exc:
            logger.exception("Error al crear usuario")
            form.add_error(None, f"Error al guardar el usuario: {exc}")
            return self.form_invalid(form)

        return self.redirect_with_timestamp()


class UserUpdateView(TimestampedSuccessUrlMixin, AdminRequiredMixin, UpdateView):
    model = User
    form_class = CustomUserChangeForm
    template_name = "user/user_form.html"
    success_url = reverse_lazy("users:usuarios")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["all_groups"] = Group.objects.all().order_by("name")
        return context

    def form_valid(self, form):
        try:
            self.object = UsuariosAdminService.update_user_from_form(form)
        except Exception as exc:
            logger.exception("Error al actualizar usuario")
            form.add_error(None, f"Error al actualizar el usuario: {exc}")
            return self.form_invalid(form)

        return self.redirect_with_timestamp()


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "user/user_confirm_delete.html"
    success_url = reverse_lazy("users:usuarios")


class GroupListView(AdminRequiredMixin, ListView):
    model = Group
    template_name = "group/group_list.html"
    context_object_name = "groups"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["table_headers"] = [{"title": "Nombre"}]
        context["table_fields"] = [{"name": "name"}]
        return context
