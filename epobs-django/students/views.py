from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from tablib import Dataset
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin
from .models import Student
from .resources import StudentResource
from finance.models import StudentAccount

class add(CreateView):
    model = Student
    fields = '__all__'
    template_name = 'student/add.html'
    added_students_list = []  # TODO: tie this to the user session instead, and clear it when they click 'done' or navigate to this page?

    def post(self, request, **kwargs):
        if 'done' in request.POST:
            return redirect('list_students')
        else:
            return super().post(request, **kwargs)

    def form_valid(self, form):
        student = form.save(commit=False)
        student.first_name = form.cleaned_data.get('first_name')
        student.last_name = form.cleaned_data.get('last_name')
        student.email = form.cleaned_data.get('email')
        student.date_of_birth = form.cleaned_data.get('date_of_birth')
        student.save()
        account = StudentAccount(student = student)  # Create the linked payment account
        account.save()
        self.added_students_list.insert(0, student)
        return render(self.request, 'student/add.html', { 'form': form, 'added_students_list': self.added_students_list } )


class edit(DeletionFormMixin, UpdateView):
    model = Student
    fields = '__all__'
    template_name = 'student/edit.html'
    success_url = '/students/'


class list(ListView):
    model = Student
    template_name = 'student/list.html'

    def post(self, request, **kwargs):
        if 'export' in request.POST:
            student_resource = StudentResource()
            dataset = student_resource.export()
            response = HttpResponse(dataset.csv, content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="students.csv"'
            return response
        elif 'import' in request.POST:
            #if 'import_students' not in request.FILES.keys():
            #if not form.is_valid():
            #    return HttpResponse("No file uploaded. Fix it, please.", content_type="text/plain") # TODO: nicer error handling
            student_resource = StudentResource()
            dataset = Dataset()
            new_students = request.FILES['import_students']
            imported_data = dataset.load(new_students.read().decode('utf-8'),format='csv') # TODO: shouldn't need to hardcode 'utf-8' or 'csv' here. Is the tablib detect_format code working correctly?
            result = student_resource.import_data(dataset, dry_run=True)  # Test the data import
            if not result.has_errors():
                student_resource.import_data(dataset, dry_run=False)  # Actually import now
            return redirect('list_students')
        else:
            return super().post(request, **kwargs)
