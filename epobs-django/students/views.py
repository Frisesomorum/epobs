from django import forms
from django.shortcuts import redirect
from django.urls import reverse_lazy
from tablib import Dataset
from core.views import DeletionFormMixin, SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView,
    SchooledUpdateView, SchoolFormMixin, )
from .models import Student
from .resources import StudentResource


class List(SchooledListView):
    permission_required = 'students.view_student'
    model = Student
    template_name = 'students/list.html'

    def get_queryset(self):
        return super().get_queryset().filter(is_enrolled=True)

    def post(self, request, **kwargs):
        if 'import' in request.POST:
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


class Detail(SchooledDetailView):
    permission_required = 'students.view_student'
    model = Student
    template_name = 'students/detail.html'
    context_object_name = 'student'


class StudentForm(SchoolFormMixin, forms.ModelForm):
    school_filter_fields = ('graduating_class', )

    class Meta:
        model = Student
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'email',
            'graduating_class', 'is_enrolled', )


class Create(SessionRecentsMixin, SchooledCreateView):
    permission_required = 'students.add_student'
    model = Student
    form_class = StudentForm
    template_name = 'students/create.html'
    success_url = reverse_lazy('student-create')

    def form_valid(self, form):
        http_response = super().form_valid(form)
        self.add_object_to_session(self.object.pk)
        return http_response


class Edit(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'students.change_student'
    model = Student
    form_class = StudentForm
    template_name = 'students/edit.html'
    success_url = reverse_lazy('student-list')
