from django.contrib.auth.views import LoginView
from django.urls import reverse


class UsuariosLoginView(LoginView):
    template_name = "user/login.html"

    def get_success_url(self):
        if self.request.user.groups.filter(name="EncargadoInstitucion").exists():
            from core.models import Institucion

            institucion = Institucion.objects.filter(
                encargados=self.request.user
            ).first()
            if institucion:
                return reverse(
                    "configuracion:institucion_detalle", kwargs={"pk": institucion.pk}
                )

        return super().get_success_url()
