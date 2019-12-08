from django.contrib import admin
from .import models

# Register your models here.
admin.site.register(models.Company)
admin.site.register(models.Company_Department)
admin.site.register(models.Company_Round)
admin.site.register(models.Company_Registration_Time)
