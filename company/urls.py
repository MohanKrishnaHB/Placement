from django.urls import path
from . import views

urlpatterns = [
    path('', views.company),
    path('add-company/', views.add_company),
    path('edit-company/', views.edit_company),
    path('delete-company/', views.delete_company),
    
    path('add-students-to-company/', views.add_students_to_company),
    path('add-student-to-company/', views.add_student_to_company),
    path('change-company-state/', views.change_company_state),
    path('change-round-title/', views.change_round_title),
    path('delete-round/', views.delete_round),
    
]