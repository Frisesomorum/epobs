from django import forms
from django.urls import reverse_lazy
from django.core.exceptions import ObjectDoesNotExist, ValidationError
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
    username = forms.CharField()
    email = forms.EmailField()
    field_order = ['username', 'email']

    class Meta:
        model = UserSchoolMembership
        fields = ('groups',)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        self.cleaned_data['user'] = None
        try:
            user = User.objects.get(username=username)
        except ObjectDoesNotExist:
            raise ValidationError(
                'There is no user with that user name.',
                code='user_not_found',
            )
        if user.email != email:
            raise ValidationError(
                '%(user)s\'s email address does not match the one you entered.',
                code='mismatched_email',
                params={'user': user},
            )
        if UserSchoolMembership.objects.filter(user=user, school=self.school).exists():
            raise ValidationError(
                '%(user)s is already a member of this school.',
                code='user_already_member',
                params={'user': user},
            )
        self.cleaned_data['user'] = user
        return self.cleaned_data

    def save(self, commit=True):
        self.instance.user = self.cleaned_data.get('user')
        return super().save(commit)


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


class CreateClass(SchooledCreateView):
    permission_required = 'schools.add_graduatingclass'
    model = GraduatingClass
    fields = ('graduating_year', 'label', 'graduated')
    template_name = 'schools/classes/create.html'


class EditClass(DeletionFormMixin, SchooledUpdateView):
    permission_required = 'schools.change_graduatingclass'
    model = GraduatingClass
    fields = ('graduating_year', 'label', 'graduated')
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
        return super().form_valid(self.get_form())

    def form_invalid(self, fee_formset):
        return super().form_invalid(self, self.get_form())
