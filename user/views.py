from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
from .models import User, User_Permissions
from student.models import BE_Student_Marks, MBA_Student_Marks, MCA_Student_Marks, Student

# Create your views here.
def users(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        users = User.objects.all()
        #return render(request, 'users.html', {'user':True, 'users':users, 'user': user})
        return redirect('/users/more/')
    return redirect('/users/log-in')

def log_in(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(user_id=username, password=password).exists():
            user = User.objects.get(user_id=username, password=password)
            request.session['user'] = username
            return redirect('/')
        if Student.objects.filter(USN=username).exists():
            student = Student.objects.get(USN=username)
            if password == student.password:
                request.session['student'] = student.USN
                return redirect('/student/home/')
        messages.info(request, 'Invalid user details')
        return redirect('/users/log-in')
    else:
        registration_open = User_Permissions.objects.all()[0].registration_open
        return render(request, 'log_in.html', {'registration_open':registration_open })

def log_out(request):
    request.session.flush()
    return redirect('/users/log-in')

def change_password(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    if not (request.session.has_key('user')):
        return redirect('/users/log-in')
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        if user.password == old_password:
            user.password = new_password
            user.save()
            messages.info(request, 'Password Changed Successfully')
        else:
            messages.info(request, 'Incorrect Current Password')
        return redirect('/student/')
        
def add_user(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        user_id = request.POST['user_id']
        user_name = request.POST['user_name']
        department = request.POST['department']
        password = request.POST['password']
        user_type = request.POST['user_type']
        user = User(user_id=user_id, name=user_name, password=password, department=department, user_type=user_type)
        user.save()
        return redirect('/users/more/')
    return redirect('/users/log-in')

def delete_user(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() and request.GET.get('user_id', False):
        user_id = request.GET['user_id']
        user = User.objects.get(user_id=user_id)
        user.delete()
        return redirect('/users/more')
    return redirect('/users/log-in')

def more(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        users = User.objects.all()
        permission = User_Permissions.objects.all()[0]
        return render(request, 'more.html', {'more': True, 'user': user, 'users': users, 'permission': permission})
    return redirect('/users/log-in')

def change_permission(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() and request.GET.get('permission_number', False) and request.GET.get('status', False):
        permission_number = request.GET.get('permission_number', False)
        status = request.GET.get('status', False)
        permission = User_Permissions.objects.all()[0]
        if permission_number == '1':
            permission.coordinator_edit_student_details = status
        elif permission_number == '2':
            permission.students_edit_their_details = status
        elif permission_number == '3':
            permission.add_students_to_company = status
        elif permission_number == '4':
            permission.registration_open = status
        permission.save()
        return HttpResponse('true')
    return redirect('/users/log-in')