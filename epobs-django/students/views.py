from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.mixins import PermissionRequiredMixin
from tablib import Dataset
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from epobs.views import DeletionFormMixin, SessionRecentsMixin
from .models import Student
from .resources import StudentResource
from finance.models import StudentAccount

class add(PermissionRequiredMixin, SessionRecentsMixin, CreateView):
    permission_required = 'students.add_student'
    model = Student
    fields = '__all__'
    template_name = 'student/add.html'
    success_url = '/students/'

    def form_valid(self, form):
        student = form.save()
        self.add_object_to_session(student.pk)
        account = StudentAccount.objects.create(student = student)  # Create the linked payment account
        return HttpResponseRedirect(self.request.path_info)  # Return the user to this page with a fresh form


class edit(PermissionRequiredMixin, DeletionFormMixin, UpdateView):
    permission_required = 'students.change_student'
    model = Student
    fields = '__all__'
    template_name = 'student/edit.html'
    success_url = '/students/'


class list(PermissionRequiredMixin, ListView):
    permission_required = 'students.view_student'
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
