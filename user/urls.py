from django.urls import path
from . import views

urlpatterns = [
    path('', views.users),
    path('log-in/', views.log_in),
    path('log-out/', views.log_out),
    path('change-password/', views.change_password),
    path('add-user/', views.add_user),
    path('delete-user/', views.delete_user),
    path('more/', views.more),
    path('change-permission/', views.change_permission),
    
]