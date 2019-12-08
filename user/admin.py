from django.contrib import admin
from .models import User, User_Permissions

# Register your models here.
admin.site.register(User)
admin.site.register(User_Permissions)
