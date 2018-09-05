from django.http import HttpResponseRedirect
from core.views import DeletionFormMixin, SessionRecentsMixin
from schools.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, get_school, )
from ..models import Supplier


class List(SchooledListView):
    permission_required = 'personnel.view_supplier'
    model = Supplier
    template_name = 'personnel/suppliers/list.html'


class Add(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'personnel.add_supplier'
    model = Supplier
    fields = ('name', 'date_hired', 'date_terminated')
    template_name = 'personnel/suppliers/add.html'
    success_url = '/personnel/suppliers/'

    def form_valid(self, form):
        supplier = form.save(commit=False)
        supplier.school = get_school(self.request.session)
        supplier.save()
        self.add_object_to_session(supplier.pk)
        # Return the user to this page with a fresh form
        return HttpResponseRedirect(self.request.path_info)


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'personnel.change_supplier'
    model = Supplier
    fields = ('name', 'date_hired', 'date_terminated')
    template_name = 'personnel/suppliers/edit.html'
    success_url = '/personnel/suppliers/'
