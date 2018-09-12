from django.core.exceptions import PermissionDenied
from functools import wraps
from .views import get_school


def school_permission_required(perm):
    def decorator(function):
        @wraps(function)
        def check_school_perms(request, *args, **kwargs):
            if isinstance(perm, str):
                perms = (perm,)
            else:
                perms = perm
            school = get_school(request.session)
            if not request.user.has_school_perms(perms, school):
                raise PermissionDenied
            return function(request, *args, **kwargs)
        return check_school_perms
    return decorator
