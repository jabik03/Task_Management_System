from django.core.exceptions import PermissionDenied


def role_required(allowed_roles=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role not in allowed_roles:
                raise PermissionDenied("У вас нет прав для этого действия.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
