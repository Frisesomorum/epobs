from django.shortcuts import render, redirect, get_object_or_404
from .models import Student
from django.views.generic.edit import CreateView, UpdateView

class add(CreateView):
    model = Student
    fields = '__all__'
    template_name = 'student/add.html'
    added_students_list = []  # TODO: tie this to the user session instead, and clear it when they click 'done' or navigate to this page?

    def form_valid(self, form):
        student = form.save(commit=False)
        student.first_name = form.cleaned_data.get('first_name')
        student.last_name = form.cleaned_data.get('last_name')
        student.email = form.cleaned_data.get('email')
        student.date_of_birth = form.cleaned_data.get('date_of_birth')
        student.save()
        self.added_students_list.insert(0, student)
        return render(self.request, 'student/add.html', { 'form': form, 'added_students_list': self.added_students_list } )


class edit(UpdateView):
    model = Student
    fields = '__all__'
    template_name = 'student/edit.html'
    success_url = '/students/'

    def post(self, request, **kwargs):
        if 'delete' in request.POST:
            student = get_object_or_404(Student, pk=pk)
            student.delete()
            return redirect('view_students')
        elif 'cancel' in request.POST:
            return redirect('view_students')


def view(request):
    students = Student.objects.all()
    return render(request, 'student/view.html', {'students': students})
