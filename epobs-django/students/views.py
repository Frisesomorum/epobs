from django import forms
from django.urls import reverse_lazy
from core.lib import QueryStringArg
from core.views import DeletionFormMixin, SessionRecentsMixin, ImportTool
from schoolauth.views import (
    SchooledListView, SchooledDetailView, SchooledCreateView,
    SchooledUpdateView, SchoolFormMixin, )
from schools.models import GraduatingClass
from .models import Student
from .resources import StudentResource


STUDENT_GRADUATING_YEAR = QueryStringArg(
    url_arg='graduating_year',
    queryset_arg='graduating_year',
    display_name='Graduating Year',
    type=int
)

STUDENT_IS_ENROLLED = QueryStringArg(
    url_arg='is_enrolled',
    queryset_arg='is_enrolled',
    display_name='Enrolled',
    default=1,
    type=bool
)


class List(SchooledListView):
    permission_required = 'students.view_student'
    model = Student
    template_name = 'students/list.html'
    querystring_args = (STUDENT_GRADUATING_YEAR, STUDENT_IS_ENROLLED, )


class Detail(SchooledDetailView):
    permission_required = 'students.view_student'
    model = Student
    template_name = 'students/detail.html'
    context_object_name = 'student'

    def get_context_data(self, **kwargs):
        context = {}
        balances = self.get_object().account.balance_due_by_ledger_account()
        context['balances'] = balances
        context['total_balance'] = sum(balances.values())
        return super().get_context_data(**context)


class GraduatingClassSelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            graduating_class = GraduatingClass.objects.get(pk=int(value))
            option['attrs']['graduating_year'] = graduating_class.graduating_year
        return option


class StudentForm(SchoolFormMixin, forms.ModelForm):
    graduating_class = forms.ModelChoiceField(
        queryset=None, label='Class', required=False, widget=GraduatingClassSelect)

    class Meta:
        model = Student
        fields = (
            'first_name', 'last_name', 'date_of_birth', 'email',
            'graduating_year', 'is_enrolled', 'external_id', )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['graduating_class'].queryset = GraduatingClass.objects.filter(school=self.school).all()


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


class Import(ImportTool):
    permission_required = ('students.add_student', 'students.change_student', )
    model = Student
    resource_class = StudentResource
    success_url = reverse_lazy('student-list')
