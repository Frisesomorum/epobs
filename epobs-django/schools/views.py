from django import forms
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.views.generic.edit import CreateView
from core.views import DeletionFormMixin
from core.lib import QueryStringArg
from schoolauth.views import (
    SchooledListView, SchooledCreateView, SchooledUpdateView, SchoolFormMixin, )
from .models import GraduatingClass
from finance.models import RevenueLedgerAccount, SchoolFee
from schoolauth.models import User, UserSchoolMembership
from schoolauth.views import get_school


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
    template_name = 'accounts/user_create.html'

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

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['fee_list'] = list(RevenueLedgerAccount.objects.filter(is_student_fee=True))
        context['fees'] = {}
        for graduating_class in context['object_list']:
            context['fees'][graduating_class] = {}
            for ledger_account in context['fee_list']:
                school_fee = SchoolFee.objects.get_or_create(
                    graduating_class=graduating_class, ledger_account=ledger_account)[0]
                context['fees'][graduating_class][ledger_account] = school_fee.amount
        return context


SchoolFeeFormSet = forms.inlineformset_factory(
    GraduatingClass, SchoolFee, exclude=('graduating_year', 'ledger_account'),
    extra=0, can_delete=False)


class EditClass(SchooledUpdateView):
    permission_required = 'schools.change_graduatingclass'
    model = GraduatingClass
    fields = ('label', 'graduated')
    template_name = 'schools/classes/edit.html'
    success_url = reverse_lazy('class-list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        class_pk = self.kwargs['pk']
        graduating_class = GraduatingClass.objects.get(pk=class_pk)

        for ledger in RevenueLedgerAccount.objects.filter(is_student_fee=True).all():
            SchoolFee.objects.get_or_create(graduating_class=graduating_class, ledger_account=ledger)

        context['fee_formset'] = SchoolFeeFormSet(instance=graduating_class)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'cancel' in request.POST:
            return redirect(self.get_success_url())
        else:
            class_pk = self.kwargs['pk']
            graduating_class = GraduatingClass.objects.get(pk=class_pk)
            fee_formset = SchoolFeeFormSet(
                request.POST, instance=graduating_class)
            if not fee_formset.is_valid():
                return self.form_invalid(fee_formset)
            return self.form_valid(fee_formset)

    def form_valid(self, fee_formset):
        fee_formset.save()
        self.object = self.get_object()
        return redirect(self.get_success_url())

    def form_invalid(self, fee_formset):
        self.object = self.get_object()
        return self.render_to_response(self.get_context_data())
