from django.db import models
from decimal import Decimal

# Create your models here.
class Student(models.Model):
    gender_choice = (('Male','Male'),('Female','Female'))
    status_choice = (('inactive','inactive'), ('active','active'))
    department_choice = (('ISE','ISE'), ('CSE','CSE'), ('ECE','ECE'), ('MEC','MEC'), ('CIV','CIV'), ('MBA','MBA'), ('MCA','MCA'))

    USN = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=50)
    department = models.CharField(max_length=10, choices=department_choice)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=15)
    date_of_birth = models.DateField(auto_now=False, auto_now_add=False, null=True)
    gender = models.CharField(max_length=10, choices=gender_choice, default='Male')
    status = models.CharField(max_length=10, choices=status_choice, default='active')
    password = models.CharField(max_length=50, default="placements_mitm")
    last_edited_by = models.CharField(max_length=50, default="registered")

    def __str__(self):
        return str(self.USN)
        
class BE_Student_Marks(models.Model):
    puc_choice = (('PUC','PUC'), ('Diploma','Diploma'))

    USN = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    SSLC_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    PUC_or_diploma = models.CharField(max_length=10, choices=puc_choice, default='PUC')
    PUC_or_diploma_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    CGPA = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))

class MCA_Student_Marks(models.Model):
    puc_choice = (('PUC','PUC'), ('Diploma','Diploma'))

    USN = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    SSLC_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    PUC_or_diploma = models.CharField(max_length=10, choices=puc_choice, default='PUC')
    PUC_or_diploma_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    BCA_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    CGPA = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))

class MBA_Student_Marks(models.Model):
    puc_choice = (('PUC','PUC'), ('Diploma','Diploma'))
    bba_choice = (('BCOM','BCOM'), ('BBA','BBA'))
    finance_choice = (('Finance','Finance'), ('Management','Management'))

    USN = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    SSLC_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    PUC_or_diploma = models.CharField(max_length=10, choices=puc_choice, default='PUC')
    PUC_or_diploma_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    BBA_or_BCOM = models.CharField(max_length=10, choices=bba_choice, default='BBA')
    Finance_or_Management = models.CharField(max_length=10, choices=finance_choice, default='Finance')
    BBA_or_BCOM_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    CGPA = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))

