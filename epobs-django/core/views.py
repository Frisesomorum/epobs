from django.shortcuts import render, redirect
from schoolauth.views import get_school_pk


def index_view(request):
    return render(request, 'index.html')


class DeletionFormMixin:

    # The combined edit/delete view expects a form
    # that includes buttons named 'delete' and 'cancel'.
    def post(self, request, **kwargs):
        if 'delete' in request.POST:
            self.object = self.get_object()
            self.object.delete()
            return redirect(self.get_success_url())
        elif 'cancel' in request.POST:
            self.object = self.get_object()
            return redirect(self.get_success_url())
        else:
            return super().post(request, **kwargs)


class SessionRecentsMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.session_recents_key in self.request.session:
            context[self.context_recents_key] = [
                self.model.objects.get(pk=pk)
                for pk in self.request.session[self.session_recents_key]
            ]
        return context

    def add_object_to_session(self, pk):
        if self.session_recents_key not in self.request.session:
            self.request.session[self.session_recents_key] = []
        self.request.session[self.session_recents_key] = [pk] + self.request.session[self.session_recents_key]

    @property
    def session_recents_key(self):
        return (
            'recent_school%s_%s_list' % (
                str(get_school_pk(self.request.session)),
                self.model.__name__.lower()
            )
        )

    @property
    def context_recents_key(self):
        return 'recent_%s_list' % self.model.__name__.lower()
