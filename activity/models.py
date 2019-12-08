from django.db import models
from company.models import Company, Company_Round
from student.models import Student
# Create your models here.
class Student_Company_Registration(models.Model):
    status_choice = (('Registered','Registered'),('Rejected','Rejected'),('Not-Registered','Not-Registered'))

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=status_choice, default='Not-Registered')

class Student_Company_Round(models.Model):
    status_choice = (('Pass','Pass'),('Fail','Fail'),('Not-Attended','Not-Attended'))

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company_round = models.ForeignKey(Company_Round, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=status_choice, default='Not-Attended')

class Student_Placed(models.Model):
    department_choice = (('ISE','ISE'), ('CSE','CSE'), ('ECE','ECE'), ('MEC','MEC'), ('CIV','CIV'), ('MBA','MBA'), ('MCA','MCA'))

    USN = models.CharField(max_length=20)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=20, choices=department_choice)
    phone = models.CharField(max_length=15)
    company = models.CharField(max_length=80)
    package = models.CharField(max_length=20)
