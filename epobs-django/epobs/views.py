from django.shortcuts import render, redirect
from django.views.generic.edit import UpdateView

def index(request):

	return render(request, 'index.html')

class UpdateDeleteView(UpdateView):

    def post(self, request, **kwargs):
        if 'delete' in request.POST:
            self.get_object().delete()
            return redirect(self.success_url)
        elif 'cancel' in request.POST:
            return redirect(self.success_url)
        else:
            return super().post(request, **kwargs)
