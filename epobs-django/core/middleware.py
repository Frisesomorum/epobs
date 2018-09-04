from django.urls import reverse
from django.http import HttpResponseRedirect
from django.conf import settings
from re import compile


class LoginRequiredMiddleware:
    login_exempt_urls = [compile(settings.LOGIN_URL.lstrip('/'))]
    school_context_exempt_urls = [compile('logout/'), compile('selectschool/')]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        assert hasattr(request, 'user')
        if not request.user.is_authenticated:
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in self.login_exempt_urls):
                return HttpResponseRedirect(reverse(settings.LOGIN_URL))
        elif 'school' not in request.session.keys():
            path = request.path_info.lstrip('/')
            if not any(m.match(path) for m in self.school_context_exempt_urls):
                return HttpResponseRedirect(reverse('select_school'))
        return self.get_response(request)
