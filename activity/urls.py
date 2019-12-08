from django.urls import path
from . import views

urlpatterns = [
    path('', views.activity),
    path('change-student-status/', views.change_student_status),
    path('student-list/', views.student_list),
    path('change-round-state/', views.change_round_state),
    path('register-all/', views.register_all),
    path('final-report/', views.final_report),
    
]