from asgiref.sync import sync_to_async
from django.utils.asyncio import async_unsafe

@async_unsafe
def user_groups(request):
    """Context processor para pasar los grupos del usuario al template"""
    if request.user.is_authenticated:
        try:
            groups = list(request.user.groups.values_list('name', flat=True))
        except Exception:
            groups = []
        return {
            'user_groups_list': groups,
            'user_groups_json': str(groups).replace("'", '"')
        }
    return {
        'user_groups_list': [],
        'user_groups_json': '[]'
    }