from django.shortcuts import render, redirect, HttpResponse
from .models import Company, Company_Department, Company_Round, Company_Registration_Time
from student.models import Student, BE_Student_Marks, MBA_Student_Marks, MCA_Student_Marks
from activity.models import Student_Company_Registration, Student_Company_Round, Student_Placed
from user.models import User, User_Permissions
from decimal import Decimal
# Create your views here.
def company(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
            permission = User_Permissions.objects.all()[0]
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() or user.is_coordinator() or user.is_other():
        branches = ['ISE', 'CSE', 'ECE', 'MEC', 'CIV', 'MCA', 'MBA']
        if user.department != 'Placement' and user.department != 'other':
            branches = [user.department]
        companies = Company.objects.all()
        for company in companies:
            rounds = Company_Round.objects.filter(company=company)
            company.rounds = []
            students_placed = 0
            for round in rounds:
                students_placed = len(Student_Company_Round.objects.filter(company_round=round, status='Pass'))
                temp = {'title': round.round_title, 'date': round.round_date}
                company.rounds.append(temp)
                company.finished = round.status
            company.students_registered = len(Student_Company_Registration.objects.filter(company__id=company.id, status='Registered'))
            company.students_placed = students_placed
            branches = Company_Department.objects.filter(company=company)
            company.branches = []
            for branch in branches:
                company.branches.append(branch.department)
            company.eligible = []
            for branch in company.branches:
                company.eligible.append(len(Student_Company_Registration.objects.filter(company=company, student__department=branch)))
            company.registration = Company_Registration_Time.objects.get(company__id=company.id)
        return render(request, 'company.html', {'company': True, 'user': user, 'companies': companies, 'permission': permission})
    else:
        return redirect('/users/log-in/')

def add_company(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        if request.method == 'POST':
            company_name = request.POST['company_name']
            description = request.POST['description']
            venue = request.POST['venue']
            date_of_visit = request.POST['date_of_visit']
            package = request.POST['package']

            try:
                min_sslc = Decimal(request.POST['min_sslc'])
                min_puc = Decimal(request.POST['min_puc'])
                min_cgpa = Decimal(request.POST['min_cgpa'])
            except:
                min_sslc = Decimal('0')
                min_puc = Decimal('0')
                min_cgpa = Decimal('0')
            try:
                max_sslc = Decimal(request.POST['max_sslc'])
                max_puc = Decimal(request.POST['max_puc'])
                max_cgpa = Decimal(request.POST['max_cgpa'])
            except:
                max_sslc = Decimal('100')
                max_puc = Decimal('100')
                max_cgpa = Decimal('10')
            company = Company(company_name=company_name, description=description, venue=venue, date_of_visit=date_of_visit, min_SSLC_percentage=min_sslc, min_PUC_percentage=min_puc, min_CGPA=min_cgpa, max_SSLC_percentage=max_sslc, max_PUC_percentage=max_puc, max_CGPA=max_cgpa, package=package)
            company.save()

            ''' Add Departments Allowed '''
            branches = ['ISE', 'CSE', 'ECE', 'MEC', 'CIV', 'MCA', 'MBA']
            branches_allowed = []
            for branch in branches:
                if request.POST.get(branch, False):
                    try:
                        company_branch = Company_Department(company=company, department=branch)
                        branches_allowed.append(branch)
                        company_branch.save()
                    except:
                        company.delete()
                        break

            ''' Add Rounds '''
            number_of_rounds = int(request.POST['number_of_rounds'])
            for i in range(1, number_of_rounds+1):
                try:
                    round_name = request.POST['round'+str(i)]
                    round_date = request.POST['round'+str(i)+'_date']
                    round_type = request.POST['round'+str(i)+'_type']
                    company_round = Company_Round(company=company, order=i, round_title=round_name, round_date=round_date, round_type=round_type)
                    company_round.save()
                except:
                    company.delete()
                    break

            ''' Add Students To Company '''
            if Company.objects.filter(company_name=company_name).exists():
                for branch in branches_allowed:
                    if branch in ['ISE', 'CSE', 'ECE', 'MEC', 'CIV']:
                        students = BE_Student_Marks.objects.filter(USN__status='active', USN__department=branch, SSLC_percentage__gte=min_sslc, PUC_or_diploma_percentage__gte=min_puc, CGPA__gte=min_cgpa, SSLC_percentage__lte=max_sslc, PUC_or_diploma_percentage__lte=max_puc, CGPA__lte=max_cgpa)
                        for student in students:
                            s = Student.objects.get(USN=student.USN.USN)
                            register = Student_Company_Registration(company=company, student=s, status='Not-Registered')
                            register.save()
                    if branch == 'MCA':
                        students = MCA_Student_Marks.objects.filter(USN__status='active', USN__department=branch, SSLC_percentage__gte=min_sslc, PUC_or_diploma_percentage__gte=min_puc, BCA_percentage__gte=min_puc, CGPA__gte=min_cgpa, SSLC_percentage__lte=max_sslc, PUC_or_diploma_percentage__lte=max_puc, BCA_percentage__lte=max_puc, CGPA__lte=max_cgpa)
                        for student in students:
                            s = Student.objects.get(USN=student.USN.USN)
                            register = Student_Company_Registration(company=company, student=s, status='Not-Registered')
                            register.save()
                    if branch == 'MBA':
                        students = MBA_Student_Marks.objects.filter(USN__status='active', USN__department=branch, SSLC_percentage__gte=min_sslc, PUC_or_diploma_percentage__gte=min_puc, BBA_or_BCOM_percentage__gte=min_puc, CGPA__gte=min_cgpa, SSLC_percentage__lte=max_sslc, PUC_or_diploma_percentage__lte=max_puc, BBA_or_BCOM_percentage__lte=max_puc, CGPA__lte=max_cgpa)
                        for student in students:
                            s = Student.objects.get(USN=student.USN.USN)
                            register = Student_Company_Registration(company=company, student=s, status='Not-Registered')
                            register.save()

            ''' Add Registration Timings '''
            start_time = request.POST['registration_start_time']
            end_time = request.POST['registration_end_time']
            try:
                company_registration_time = Company_Registration_Time(company=company, start_time=start_time, end_time=end_time)
                company_registration_time.save()
            except:
                company.delete()
            
        return redirect('/company/')
    else:
        return redirect('/users/log-in/')

''' This method recieves a company and returns a list of eligible and non-elegible students '''
def add_students_to_company(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
            permission = User_Permissions.objects.all()[0]
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() or (user.is_coordinator() and permission.add_students_to_company):
        if request.method == 'GET' and request.GET.get('company', False):
            company_id = request.GET['company']
            company = Company.objects.get(id=company_id)
            departments = Company_Department.objects.filter(company=company).values('department')
            students = Student_Company_Registration.objects.filter(company=company, student__department__in=departments).values('student')
            students_list = []

            be_selected_students = BE_Student_Marks.objects.filter(USN__in=students)
            for s in be_selected_students:
                s.selected = True
                students_list.append({'student':s, 'selected':True})
            be_students = BE_Student_Marks.objects.filter(USN__department__in=departments)
            for s in be_students:
                s.selected = False
                if not {'student':s, 'selected':True} in students_list:
                    students_list.append({'student':s, 'selected':False})
            
            mca_selected_students = MCA_Student_Marks.objects.filter(USN__in=students)
            for s in mca_selected_students:
                s.selected = True
                students_list.append({'student':s, 'selected':True})
            mca_students = MCA_Student_Marks.objects.filter(USN__department__in=departments)
            for s in mca_students:
                s.selected = False
                if not {'student':s, 'selected':True} in students_list:
                    students_list.append({'student':s, 'selected':False})

            mba_selected_students = MBA_Student_Marks.objects.filter(USN__in=students)
            for s in mba_selected_students:
                s.selected = True
                students_list.append({'student':s, 'selected':True})
            mba_students = MBA_Student_Marks.objects.filter(USN__department__in=departments)
            for s in mba_students:
                s.selected = False
                if not {'student':s, 'selected':True} in students_list:
                    students_list.append({'student':s, 'selected':False})
            
            return render(request, 'add_student_to_company.html', {'students_list': students_list, 'user': user, 'company': company})

''' This method is requested by a ajax call and recieves usn and company and adds that usn to that company in student_company_registration '''
def add_student_to_company(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
            permission = User_Permissions.objects.all()[0]
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() or (user.is_coordinator() and permission.add_students_to_company):
        if request.method == 'GET' and request.GET.get('company', False) and request.GET.get('usn', False) and request.GET.get('add', False):
            usn = request.GET.get('usn', False)
            company_name = request.GET.get('company', False)
            student = Student.objects.get(USN=usn)
            company = Company.objects.get(company_name=company_name)
            if request.GET.get('add') == 'true':
                register = Student_Company_Registration(company=company, student=student)
                register.save()
            else:
                register = Student_Company_Registration.objects.get(company=company, student=student)
                register.delete()
            return HttpResponse('Success')
    return redirect('/users/log-in')

def change_company_state(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        if request.GET.get('company', False):
            company_id = request.GET.get('company', False)
            company = Company.objects.get(id=company_id)
            if company.status == '2':
                rounds = Company_Round.objects.filter(company=company)
                round = None
                for r in rounds:
                    round = r
                students_placed = Student_Company_Round.objects.filter(company_round=round, status='Pass')
                for student in students_placed:
                    usn = student.student.USN
                    name = student.student.name
                    department = student.student.department
                    phone = student.student.phone
                    company_name = company.company_name
                    package = company.package
                    place = Student_Placed(USN=usn, name=name, department=department, phone=phone, company=company_name, package=package)
                    place.save()
                    student_temp = Student.objects.get(USN=student.student.USN)
                    student_temp.status = 'inactive'
                company.status = '1'
                company.save()
            if company.status == '0':
                company.status = '2'
                company.save()
            return redirect('/company/')
    return redirect('/users/log-in')

def change_round_title(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        if request.GET.get('round_id', False) and request.GET.get('new_title', False) and request.GET.get('date', False):
            round_id = request.GET.get('round_id', False)
            round = Company_Round.objects.get(id=round_id)
            round.round_title = request.GET.get('new_title', False)
            round.round_date = request.GET.get('date', False)
            round.round_type = request.GET.get('type', False)
            round.save()
            round = Company_Round.objects.get(id=round_id)
            return HttpResponse(round.round_title)
        return redirect('/company/')
    return redirect('/users/log-in')

def edit_company(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():

        return render(request, 'edit_company.html')
    return redirect('/users/log-in')

def delete_round(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        if request.GET.get('round_id', False) and request.GET.get('company_id', False):
            round_id = request.GET.get('round_id', False)
            round = Company_Round.objects.get(id=round_id)
            round.delete()
        return redirect('/activity/?company='+str(request.GET.get('company_id', False)))
    return redirect('/users/log-in')

def delete_company(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        if request.GET.get('company_id', False):
            company_id = request.GET.get('company_id', False)
            company = Company.objects.get(id=company_id)
            company.delete()
        return redirect('/company/')
    return redirect('/users/log-in')

