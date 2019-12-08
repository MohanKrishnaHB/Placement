from django.db import models

# Create your models here.
class User(models.Model):
    user_types = (('admin', 'admin'), ('co-ordinator', 'co-ordinator'), ('other', 'other'))
    department_choice = (('Placement','Placement'), ('ISE','ISE'), ('CSE','CSE'), ('ECE','ECE'), ('MEC','MEC'), ('CIV','CIV'), ('MBA','MBA'), ('MCA','MCA'))

    user_id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=50)
    password = models.CharField(max_length=257)
    department = models.CharField(max_length=10, choices=department_choice)
    user_type = models.CharField(max_length=20, choices=user_types, default='co-ordinator')

    def __str__(self):
        return self.name
    def is_admin(self):
        if self.user_type == 'admin':
            return True
        return False
    def is_coordinator(self):
        if self.user_type == 'co-ordinator':
            return True
        return False
    def is_other(self):
        if self.user_type == 'other':
            return True
        return False

  
class User_Permissions(models.Model):
    coordinator_edit_student_details = models.BooleanField(default=True)
    students_edit_their_details = models.BooleanField(default=False)
    add_students_to_company = models.BooleanField(default=False)
    registration_open = models.BooleanField(default=True)