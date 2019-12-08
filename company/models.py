from django.db import models
from decimal import Decimal
from datetime import datetime
# Create your models here.
class Company(models.Model):
    status_choice = (('0','Not-active'),('2','Active'),('1','Finished'))
    
    company_name = models.CharField(max_length=50)
    description = models.TextField()
    venue = models.CharField(max_length=50, default='MITM')
    date_of_visit = models.DateField(auto_now=False, auto_now_add=False)
    min_SSLC_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    min_PUC_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))
    min_CGPA = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.00'))
    max_SSLC_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'))
    max_PUC_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('100.00'))
    max_CGPA = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('10.00'))
    package = models.CharField(max_length=10, default='Open')
    status = models.CharField(max_length=1, choices=status_choice, default='0')

    def __str__(self):
        return str(self.company_name)
    def is_active(self):
        if self.status == '2':
            return True
        return False
    def is_inactive(self):
        if self.status == '0':
            return True
        return False
    def is_finished(self):
        if self.status == '1':
            return True
        return False
    

class Company_Department(models.Model):
    department_choice = (('ISE','ISE'), ('CSE','CSE'), ('ECE','ECE'), ('MEC','MEC'), ('CIV','CIV'), ('MBA','MBA'), ('MCA','MCA'))

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    department = models.CharField(max_length=10, choices=department_choice)

class Company_Round(models.Model):
    status_choice = (('1','Not-active'),('2','Active'),('0','Finished'))
    round_type_choice = (('Aptitude','Aptitude'),('Technical','Technical'),('Discussion','Discussion'),('Interview','Interview'))
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    order = models.IntegerField()
    round_title = models.CharField(max_length=80)
    round_date = models.DateField(auto_now=False, auto_now_add=False)
    round_type = models.CharField(max_length=30, choices=round_type_choice, default='Aptitude')
    status = models.CharField(max_length=15, choices=status_choice, default='1')

class Company_Registration_Time(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    end_time = models.DateTimeField(auto_now=False, auto_now_add=False)
    
    def is_registration_open(self):
        start = str(self.start_time)[:19]
        end = str(self.end_time)[:19]
        now = str(datetime.now())[:19]
        start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        end = datetime.strptime(end, '%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        if start <= now and end  >= now:
            return True
        return False

    def is_registration_not_open_yet(self):
        start = str(self.start_time)[:19]
        now = str(datetime.now())[:19]
        start = datetime.strptime(start, '%Y-%m-%d %H:%M:%S')
        now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')
        if start >= now:
            return True
        return False