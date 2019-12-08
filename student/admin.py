from django.contrib import admin
from .import models

# Register your models here.
admin.site.register(models.Student)
admin.site.register(models.BE_Student_Marks)
admin.site.register(models.MBA_Student_Marks)
admin.site.register(models.MCA_Student_Marks)
