from django.shortcuts import render
from .models import Student
from .forms import NewStudentForm

def edit(request):
    students = Student.objects.all()
    if request.method == 'POST':
        form = NewStudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.first_name = form.cleaned_data.get('first_name')
            student.last_name = form.cleaned_data.get('last_name')
            student.email = form.cleaned_data.get('email')
            student.date_of_birth = form.cleaned_data.get('date_of_birth')
            student.save()
    else:
        form = NewStudentForm()
    return render(request, 'students.html', {'students': students, 'form': form})
