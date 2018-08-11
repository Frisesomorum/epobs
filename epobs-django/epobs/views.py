from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView

def index(request):

    return render(request, 'index.html')

    """ The combined edit/delete view expects a form
    that includes buttons named 'delete' and 'cancel'.
    """
class DeletionFormMixin:

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

    def post(self, request, **kwargs):
        if 'done' in request.POST:
            return redirect(self.success_url)
        else:
            return super().post(request, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.recents_key in self.request.session:
            context[self.recents_key] = [ self.model.objects.get(pk=pk)
                for pk in self.request.session[self.recents_key]
            ]
        return context

    def add_object_to_session(self, pk):
        if self.recents_key not in self.request.session:
            self.request.session[self.recents_key] = []
        self.request.session[self.recents_key] = [pk] + self.request.session[self.recents_key]

    @property
    def recents_key(self):
        return 'recent_' + self.model.__name__.lower() + 's_list'
