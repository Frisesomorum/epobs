from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.http import HttpResponse
from tablib import Dataset
from core.views import DeletionFormMixin, SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, )
from .models import Student
from .resources import StudentResource


class List(SchooledListView):
    permission_required = 'students.view_student'
    model = Student
    template_name = 'students/list.html'

    def post(self, request, **kwargs):
        if 'export' in request.POST:
            student_resource = StudentResource()
            dataset = student_resource.export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="students.csv"'
            return response
        elif 'import' in request.POST:
            # TODO: nicer error handling
            student_resource = StudentResource()
            dataset = Dataset()
            new_students = request.FILES['import_students']
            # TODO: shouldn't need to hardcode 'utf-8' or 'csv' here.
            # Is the tablib detect_format code working correctly?
            dataset.load(new_students.read().decode('utf-8'), format='csv')
            # Test the data import
            result = student_resource.import_data(dataset, dry_run=True)
            if not result.has_errors():
                # Actually import now
                student_resource.import_data(dataset, dry_run=False)
            return redirect('student-list')
        else:
            return super().post(request, **kwargs)


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'students.add_student'
    model = Student
    fields = ('first_name', 'last_name', 'date_of_birth', 'email')
    template_name = 'students/create.html'
    success_url = reverse_lazy('student-create')

    def form_valid(self, form):
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'students.change_student'
    model = Student
    fields = ('first_name', 'last_name', 'date_of_birth', 'email')
    template_name = 'students/edit.html'
    success_url = reverse_lazy('student-list')
