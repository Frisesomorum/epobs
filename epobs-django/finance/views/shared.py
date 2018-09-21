from schoolauth.views import SchooledCreateView, SchooledUpdateView


class RequiresApprovalMixin:
    def form_valid(self, form):
        http_response = super().form_valid(form)
        if 'save-and-submit' in self.request.POST:
            self.object.submit_for_approval(self.request.user)
        return http_response


class RequiresApprovalCreateView(RequiresApprovalMixin, SchooledCreateView):
    pass


class RequiresApprovalUpdateView(RequiresApprovalMixin, SchooledUpdateView):
    def dispatch(self, request, *args, **kwargs):
        self.get_object().verify_can_be_edited()
        return super().dispatch(request, *args, **kwargs)
