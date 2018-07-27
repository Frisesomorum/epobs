from django.shortcuts import render, redirect, get_object_or_404
from .models import Student
from .forms import AddStudentForm, EditStudentForm

def view(request):
    students = Student.objects.all()
    return render(request, 'student/view.html', {'students': students})

def add(request):
    if request.method == 'POST':
        form = AddStudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.first_name = form.cleaned_data.get('first_name')
            student.last_name = form.cleaned_data.get('last_name')
            student.email = form.cleaned_data.get('email')
            student.date_of_birth = form.cleaned_data.get('date_of_birth')
            student.save()
    else:
        form = AddStudentForm()
    return render(request, 'student/add.html', {'form': form})

def edit(request, pk):
    student = get_object_or_404(Student, pk=pk)  # TODO: Make a nice error page for this
    if request.method == 'POST':
        form = EditStudentForm(request.POST)
        if form.is_valid():
            student.first_name = form.cleaned_data.get('first_name')
            student.last_name = form.cleaned_data.get('last_name')
            student.email = form.cleaned_data.get('email')
            student.date_of_birth = form.cleaned_data.get('date_of_birth')
            student.save()
            return redirect('view_students')
    else:
        form = EditStudentForm()
    return render(request, 'student/edit.html', {'student': student, 'form': form})
