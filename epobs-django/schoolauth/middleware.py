from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile


LOGIN_EXEMPT_URLS = [
    compile(reverse(settings.LOGIN_URL).lstrip('/')),
    compile(reverse('terms-of-service').lstrip('/')),
    compile(reverse('password_reset').lstrip('/')),
    compile(reverse('password_reset_done').lstrip('/')),
    compile(reverse('password_reset_complete').lstrip('/')),
    compile(r'accounts/reset/\w+/\w+/$'),  # 'password_reset_confirm'
    ]
SCHOOL_CONTEXT_EXEMPT_URLS = [
    compile(reverse('logout').lstrip('/')),
    compile(reverse('school-select').lstrip('/')),
    ]


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, 'user')
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in LOGIN_EXEMPT_URLS):
                return HttpResponseRedirect(reverse(settings.LOGIN_URL))
        elif 'school_pk' not in request.session.keys():
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in SCHOOL_CONTEXT_EXEMPT_URLS):
                return HttpResponseRedirect(reverse('school-select'))
        return self.get_response(request)
