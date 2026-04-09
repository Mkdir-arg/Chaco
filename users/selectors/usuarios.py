from django.contrib.auth.models import User
from django.db.models import F


def get_usuarios_queryset():
    return (
        User.objects.select_related("profile")
        .prefetch_related("groups", "user_permissions")
        .annotate(rol=F("profile__rol"))
        .order_by("-id")
    )
