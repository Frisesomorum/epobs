from django import forms
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import PermissionRequiredMixin, UserPassesTestMixin
from django.views.generic import FormView
from django.views.generic.edit import UpdateView
from .models import School

class SelectSchoolForm(forms.Form):
    school_list = []
    is_admin = False

    def __init__(self, *args, **kwargs):
        self.school_list = kwargs.pop('schools')
        self.is_admin = kwargs.pop('is_admin')
        super().__init__(*args, **kwargs)
        self.fields['school'] = forms.ChoiceField(choices=self.make_selection_list())

    def make_selection_list(self):
        choices = ()
        for school in self.school_list:
            choices = choices + ((school, str(School.objects.get(pk=school))),)
        if self.is_admin:
            choices = choices + (('admin', '(log in as admin)'),)
        return choices

class SelectSchool(FormView):
    form_class = SelectSchoolForm
    template_name = 'select_school.html'
    success_url = '/'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['is_admin'] = user.is_staff
        context['schools'] = list(user.schools.values_list('pk', flat=True))
        return context

    # TODO: One of these is probably redundant
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        user = self.request.user
        kwargs['is_admin'] = user.is_staff
        kwargs['schools'] = list(user.schools.values_list('pk', flat=True))
        return kwargs

    def render_to_response(self, context, **kwargs):
        schools = context['schools']
        #If user is an admin and doesn't belong to any schools, set this as an admin session
        if len(schools) == 0:
            if context['is_admin']:
                setAdminMode(self.request.session)
                return redirect('/admin/')
            else:
                raise PermissionDenied("You do not have membership in any schools.")
        #If user is not admin and belongs to exactly one school, set that school
        if len(schools) == 1 and not context['is_admin']:
            setSchool(self.request.session, schools.pop())
            return redirect(self.get_success_url())
        #Else, show the selection form
        return super().render_to_response(context, **kwargs)


    def form_valid(self, form):
        user = self.request.user
        #verify that the selected is one of the user's schools
        selection = form.cleaned_data['school']
        if selection == 'admin':
            if user.is_staff:
                setAdminMode(self.request.session)
                return redirect('/admin/')
            else:
                raise PermissionDenied("You are not an admin of this site.")
        user_schools = list(user.schools.values_list('pk', flat=True))
        if user.is_school_member(selection):
            setSchool(self.request.session, selection)
            return redirect(self.get_success_url())
        raise OperationalError("You do not have membership in this school.")

def setAdminMode(session):
    session['school'] = 'admin'
    session['school_name'] = "(Administrator Mode)"
    session['is_admin'] = True

def setSchool(session, school_pk):
    session['school'] = school_pk
    session['school_name'] = str(School.objects.get(pk=school_pk))
    session['is_admin'] = False

def isAdminMode(session):
    if 'is_admin' not in session.keys():
        raise SuspiciousOperation("School context hasn't been set for this session.")
    return session['is_admin']

def getSchool(session):
    if 'school' not in session.keys():
        raise SuspiciousOperation("School context hasn't been set for this session.")
    school_pk = session['school']
    if school_pk == 'admin':
        return None
    school = School.objects.get(pk=school_pk)
    return school

class CheckSchoolContextMixin(UserPassesTestMixin):
    def test_func(self):
        return (getSchool(self.request.session) == self.get_object().school)

def get_school_object_or_404(request, klass, **kwargs):
    object = get_object_or_404(klass, **kwargs)
    if getSchool(request.session) != object.school:
        raise SuspiciousOperation("This " + type(object) + " belongs to a school to which you are not logged in to.")
    return object


class EditSchool(PermissionRequiredMixin, UpdateView):
    permission_required = 'schools.change_school'
    model = School
    fields = '__all__'
    template_name = 'edit_school.html'
    success_url = '/'
    def get_object(self):
        if isAdminMode(self.request.session):
            raise SuspiciousOperation("You are in administrator mode and cannot edit school info.")
        return getSchool(self.request.session)
