from django.shortcuts import render, redirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import UpdateView
from .models import School

@login_required
def index_view(request):
    return render(request, 'index.html')


class EditSchool(PermissionRequiredMixin, UpdateView):
    permission_required = 'epobs.change_school'
    model = School
    fields = '__all__'
    template_name = 'edit_school.html'
    success_url = '/'
    def get_object(self):
        if not School.objects.exists():
            school = School.objects.create()
        return School.objects.first()


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
