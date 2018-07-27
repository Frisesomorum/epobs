from django import forms
from .models import Student

class NewStudentForm(forms.ModelForm):

    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'date_of_birth']
