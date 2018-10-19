from django import forms
from django.urls import reverse_lazy
from core.views import DeletionFormMixin, SessionRecentsMixin
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView,
    SchooledUpdateView, SchoolFormMixin, )
from .models import Student


class List(SchooledListView):
    permission_required = 'students.view_student'
    model = Student
    template_name = 'students/list.html'

    def get_queryset(self):
        return super().get_queryset().filter(is_enrolled=True)


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
            'graduating_class', 'is_enrolled', 'external_id', )


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
