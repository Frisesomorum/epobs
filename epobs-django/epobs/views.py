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
