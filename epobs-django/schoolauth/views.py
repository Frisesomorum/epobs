from django import forms
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from .models import School
from finance.models import RequiresApproval


class SelectSchoolForm(forms.Form):
    school_list = []
    is_admin = False

    def __init__(self, *args, **kwargs):
        self.school_list = kwargs.pop('schools')
        self.is_admin = kwargs.pop('is_admin')
        super().__init__(*args, **kwargs)
        self.fields['school'] = forms.ChoiceField(
            choices=self.make_selection_list())

    def make_selection_list(self):
        choices = ()
        for school in self.school_list:
            choices = choices + ((school, str(School.objects.get(pk=school))),)
        if self.is_admin:
            choices = choices + (('admin', '(log in as admin)'),)
        return choices


class SelectSchool(FormView):
    form_class = SelectSchoolForm
    template_name = 'school_select.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_admin'] = user.is_staff
        context['schools'] = list(user.school_perms.values_list('school', flat=True))
        return context

    # TODO: One of these is probably redundant
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        kwargs['is_admin'] = user.is_staff
        kwargs['schools'] = list(user.school_perms.values_list('school', flat=True))
        return kwargs

    def render_to_response(self, context, **kwargs):
        schools = context['schools']
        # If user is an admin and doesn't belong to any schools,
        # set this as an admin session
        if len(schools) == 0:
            if context['is_admin']:
                set_admin_mode(self.request.session)
                return redirect('admin:index')
            else:
                raise PermissionDenied("You do not have membership in any schools.")
        # If user is not admin and belongs to exactly one school,
        # set that school
        if len(schools) == 1 and not context['is_admin']:
            set_school(self.request.session, schools.pop())
            return redirect(self.get_success_url())
        # Else, show the selection form
        return super().render_to_response(context, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        # Verify that the selected is one of the user's schools
        selection = form.cleaned_data['school']
        if selection == 'admin':
            if user.is_staff:
                set_admin_mode(self.request.session)
                return redirect('admin:index')
            else:
                raise PermissionDenied("You are not an admin of this site.")
        if user.is_school_member(selection):
            set_school(self.request.session, selection)
            return redirect(self.get_success_url())
        raise SuspiciousOperation("You do not have membership in this school.")


def set_admin_mode(session):
    clear_school_session_data(session)
    session['school_pk'] = 'admin'
    # session['school'] = None
    session['school_name'] = "(Administrator Mode)"


def set_school(session, school_pk):
    clear_school_session_data(session)
    session['school_pk'] = school_pk
    school = School.objects.get(pk=school_pk)
    # session['school'] = school
    session['school_name'] = str(school)


def is_admin_mode(session):
    school_pk = session.get('school_pk', None)
    if school_pk is None:
        raise SuspiciousOperation("School context hasn't been set for this session.")
    return (school_pk == 'admin')


def get_school(session, error_if_none=True):
    try:
        school_pk = session['school_pk']
    except KeyError:
        if error_if_none:
            raise SuspiciousOperation("School context hasn't been set for this session.")
        else:
            return None
    if school_pk == 'admin':
        return None
    return School.objects.get(pk=school_pk)  # TODO: Does this need to check for changes and reload from db each time?


def get_school_pk(session):
    school_pk = session.get('school_pk', None)
    if school_pk is None:
        raise SuspiciousOperation("School context hasn't been set for this session.")
    return school_pk


def get_school_object_or_404(request, klass, **kwargs):
    object = get_object_or_404(klass, **kwargs)
    if get_school(request.session) != object.school:
        raise SuspiciousOperation("This " + type(object) + " belongs to a school to which you are not logged in to.")
    return object


def register_school_session_data(session, key):
    try:
        session['school_data'].append(key)
    except KeyError:
        session['school_data'] = [key]


def clear_school_session_data(session):
    if 'school_data' in session.keys():
        for key in session['school_data']:
            try:
                del session[key]
            except KeyError:
                pass
        del session['school_data']


class SchoolPermissionMixin(PermissionRequiredMixin):
    def has_permission(self):
        perms = self.get_permission_required()
        school = get_school(self.request.session)
        if isinstance(self, DetailView) or isinstance(self, UpdateView):
            if (school != self.get_object().school):
                return False
        return self.request.user.has_school_perms(perms, school)


class SchooledListView(SchoolPermissionMixin, ListView):
    def get_queryset(self):
        return self.model.objects.filter(school=get_school(self.request.session))


class SchooledCreateView(SchoolPermissionMixin, CreateView):
    def form_valid(self, form):
        form.instance.school = get_school(self.request.session)
        return super().form_valid(form)


class SchooledDetailView(SchoolPermissionMixin, DetailView):
    pass


class SchooledUpdateView(SchoolPermissionMixin, UpdateView):
    def dispatch(self, request, *args, **kwargs):
        object = self.get_object()
        if isinstance(object, RequiresApproval):
            object.verify_can_be_edited()
        return super().dispatch(request, *args, **kwargs)
