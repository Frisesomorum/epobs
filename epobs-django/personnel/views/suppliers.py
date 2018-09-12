from django.urls import reverse_lazy
from core.views import DeletionFormMixin, SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, )
from ..models import Supplier


class List(SchooledListView):
    permission_required = 'personnel.view_supplier'
    model = Supplier
    template_name = 'personnel/suppliers/list.html'


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'personnel.add_supplier'
    model = Supplier
    fields = ('name', 'date_hired', 'date_terminated')
    template_name = 'personnel/suppliers/create.html'
    success_url = reverse_lazy('supplier-create')

    def form_valid(self, form):
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'personnel.change_supplier'
    model = Supplier
    fields = ('name', 'date_hired', 'date_terminated')
    template_name = 'personnel/suppliers/edit.html'
    success_url = reverse_lazy('supplier-list')
