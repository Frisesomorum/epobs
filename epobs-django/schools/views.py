from django import forms
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from core.views import DeletionFormMixin
from core.lib import QueryStringArg
from schoolauth.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, SchoolFormMixin, )
from .models import SchoolProfile, GraduatingClass
from schoolauth.models import User, UserSchoolMembership
from schoolauth.views import is_admin_mode, get_school


class Edit(SchooledUpdateView):
    permission_required = 'schools.change_schoolprofile'
    model = SchoolProfile
    fields = ()
    template_name = 'schools/edit.html'
    success_url = reverse_lazy('index')

    def get_object(self):
        if is_admin_mode(self.request.session):
            raise SuspiciousOperation("You are in administrator mode and cannot edit school info.")
        return get_school(self.request.session).school_profile


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2', )


class CreateUser(CreateView):
    permission_required = 'schoolauth.add_user'
    model = User
    form_class = CreateUserForm
    template_name = 'user_create.html'

    def get_success_url(self, user_membership_pk):
        return reverse_lazy('member-edit', kwargs={'pk': user_membership_pk})

    def form_valid(self, form):
        new_user = form.save()
        user_membership = UserSchoolMembership.objects.create(
            user=new_user, school=get_school(self.request.session))
        return redirect(self.get_success_url(user_membership.pk))


class ListMembership(SchooledListView):
    permission_required = 'schoolauth.view_userschoolmembership'
    model = UserSchoolMembership
    template_name = 'schools/membership/list.html'


class CreateMembershipForm(SchoolFormMixin, forms.ModelForm):
    class Meta:
        model = UserSchoolMembership
        fields = ('user', 'groups')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = self.fields[
            'user'].queryset.exclude(school_perms__school=self.school)


class CreateMembership(SchooledCreateView):
    permission_required = 'schoolauth.add_userschoolmembership'
    model = UserSchoolMembership
    form_class = CreateMembershipForm
    template_name = 'schools/membership/create.html'
    success_url = reverse_lazy('member-list')


class EditMembership(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'schoolauth.change_userschoolmembership'
    model = UserSchoolMembership
    fields = ('groups',)
    template_name = 'schools/membership/edit.html'
    success_url = reverse_lazy('member-list')


CLASS_IS_GRADUATED = QueryStringArg(
    url_arg='graduated',
    queryset_arg='graduated',
    default=0,
    type=bool
)


class ListClass(SchooledListView):
    permission_required = 'schools.view_graduatingclass'
    model = GraduatingClass
    template_name = 'schools/classes/list.html'
    querystring_args = (CLASS_IS_GRADUATED, )


class EditClass(SchooledUpdateView):
    permission_required = 'schools.change_graduatingclass'
    model = GraduatingClass
    fields = (
        'graduating_year', 'label', 'admission_fee', 'school_fee',
        'canteen_fee', 'graduated')
    template_name = 'schools/classes/edit.html'
    success_url = reverse_lazy('class-list')
