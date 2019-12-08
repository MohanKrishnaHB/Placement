from django.urls import path
from . import views

urlpatterns = [
    path('', views.student),
    path('register/', views.register),
    path('get_student_details/', views.get_student_details),
    path('add-students-file/', views.add_students),
    path('edit-student/', views.edit_student),
    path('student-summary/', views.student_summary),
    path('home/', views.student_home),
    path('companies/', views.student_companies),
    path('register-to-company/', views.register_to_company),
    path('student-change-password/', views.student_change_password)
]