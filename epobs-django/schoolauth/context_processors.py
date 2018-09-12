from itertools import chain
from django.contrib.auth.context_processors import PermWrapper
from .views import get_school_pk
from .middleware import LOGIN_EXEMPT_URLS, SCHOOL_CONTEXT_EXEMPT_URLS


def user_school_permissions(request):
    path = request.path_info.lstrip('/')
    if any(m.match(path) for m in chain(
            LOGIN_EXEMPT_URLS, SCHOOL_CONTEXT_EXEMPT_URLS)):
        return {}
    school = get_school_pk(request.session)
    if school == 'admin':
        return {}
    return {
        'school_perms': PermWrapper(request.user.get_school_membership(school)),
    }
