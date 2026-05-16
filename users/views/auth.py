from django.contrib.auth.views import LoginView


class UsuariosLoginView(LoginView):
    template_name = "user/login.html"

    def get_success_url(self):
        return super().get_success_url()
