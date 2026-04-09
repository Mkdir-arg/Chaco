from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import FormView, TemplateView

from core.selectors_geografia import get_localidades_values, get_municipios_values
from ..forms import (
    ConsultarTramiteForm,
    CrearUsuarioInstitucionForm,
    RegistroInstitucionPublicForm,
)
from ..selectors import get_portal_home_context, get_tramites_by_email
from ..services import PortalRegistroService


def _push_form_errors_to_messages(request, form):
    for field_errors in form.errors.values():
        for error in field_errors:
            messages.error(request, error)


class PortalHomeView(TemplateView):
    template_name = "portal/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_portal_home_context())
        return context


class CrearUsuarioInstitucionView(FormView):
    template_name = "portal/crear_usuario.html"
    form_class = CrearUsuarioInstitucionForm

    def form_valid(self, form):
        user = PortalRegistroService.create_pending_user(form.cleaned_data)
        self.request.session["pending_user_id"] = user.id
        messages.success(
            self.request,
            "Usuario creado exitosamente. Complete ahora los datos de su institución.",
        )
        return redirect("portal:registro_institucion")

    def form_invalid(self, form):
        _push_form_errors_to_messages(self.request, form)
        return super().form_invalid(form)


class RegistroInstitucionView(FormView):
    template_name = "portal/registro_institucion.html"
    form_class = RegistroInstitucionPublicForm

    def dispatch(self, request, *args, **kwargs):
        self.pending_user_id = request.session.get("pending_user_id")
        if not request.user.is_authenticated and not self.pending_user_id:
            return redirect("portal:crear_usuario")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        pending_user = PortalRegistroService.get_pending_user(self.pending_user_id)
        if self.pending_user_id and pending_user is None:
            messages.error(self.request, "Error: Usuario no encontrado")
            return redirect("portal:crear_usuario")

        PortalRegistroService.create_institucion_from_form(
            form,
            pending_user=pending_user,
            authenticated_user=self.request.user,
        )
        self.request.session.pop("pending_user_id", None)
        messages.success(
            self.request,
            "Solicitud enviada correctamente. Recibirá notificaciones por email.",
        )
        return redirect("portal:consultar_tramite")

    def form_invalid(self, form):
        _push_form_errors_to_messages(self.request, form)
        return super().form_invalid(form)


class ConsultarTramiteView(FormView):
    template_name = "portal/consultar_tramite.html"
    form_class = ConsultarTramiteForm

    def get(self, request, *args, **kwargs):
        return render(
            request,
            self.template_name,
            {"form": self.get_form()},
        )

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        instituciones = get_tramites_by_email(email)
        if not instituciones.exists():
            messages.error(self.request, "No se encontraron trámites con ese email")
            return render(
                self.request,
                self.template_name,
                {"form": form},
            )

        return render(
            self.request,
            self.template_name,
            {
                "form": form,
                "instituciones": instituciones,
                "email": email,
            },
        )

    def form_invalid(self, form):
        _push_form_errors_to_messages(self.request, form)
        return super().form_invalid(form)


def get_municipios(request):
    provincia_id = request.GET.get("provincia_id")
    return JsonResponse(get_municipios_values(provincia_id), safe=False)


def get_localidades(request):
    municipio_id = request.GET.get("municipio_id")
    return JsonResponse(get_localidades_values(municipio_id), safe=False)
