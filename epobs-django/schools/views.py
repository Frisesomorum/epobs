from django import forms
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.core.exceptions import SuspiciousOperation
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from core.views import DeletionFormMixin
from schoolauth.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, )
from .models import SchoolProfile
from schoolauth.models import User, UserSchoolMembership
from schoolauth.views import is_admin_mode, get_school


class Edit(SchooledUpdateView):
    permission_required = 'schools.change_schoolprofile'
    model = SchoolProfile
    fields = ('school_fee', 'canteen_fee', 'admission_fee')
    template_name = 'schools/edit.html'
    success_url = reverse_lazy('index')

    def get_object(self):
        if is_admin_mode(self.request.session):
            raise SuspiciousOperation("You are in administrator mode and cannot edit school info.")
        return get_school(self.request.session).school_profile


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', )


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


class CreateMembershipForm(forms.ModelForm):
    class Meta:
        model = UserSchoolMembership
        fields = ('user', 'groups')

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school')
        super().__init__(*args, **kwargs)
        self.fields['user'].queryset = self.fields['user'].queryset.exclude(school_perms__school=school)


class CreateMembership(SchooledCreateView):
    permission_required = 'schoolauth.add_userschoolmembership'
    model = UserSchoolMembership
    form_class = CreateMembershipForm
    template_name = 'schools/membership/create.html'
    success_url = reverse_lazy('member-list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['school'] = get_school(self.request.session)
        return kwargs


class EditMembership(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'schoolauth.change_userschoolmembership'
    model = UserSchoolMembership
    fields = ('groups',)
    template_name = 'schools/membership/edit.html'
    success_url = reverse_lazy('member-list')
