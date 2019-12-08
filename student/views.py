from django.shortcuts import render, redirect, HttpResponse
from django.contrib import messages
import datetime
from decimal import Decimal
from django.http import JsonResponse
import xlwt
import xlrd
from user.models import User, User_Permissions
from .models import Student, BE_Student_Marks, MBA_Student_Marks, MCA_Student_Marks
from activity.models import Student_Company_Registration, Student_Company_Round, Student_Placed
from company.models import Company, Company_Department, Company_Round, Company_Registration_Time
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os
# Create your views here.


def student(request):
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
        '''students = BE_Student_Marks.objects.filter(CGPA__gte=Decimal('5.85'), CGPA__lte=Decimal('6'))
        for student in students:
            student.CGPA = Decimal('6.00')
            student.save()'''
        return render(request, 'student.html', {'student': True, 'branches': branches, 'user': user, 'permission': permission})
    return redirect('/users/log-in/')


def get_student_details(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() or user.is_coordinator() or user.is_other():
        if request.GET.get('branches', False) and request.GET.get('marks', False):
            branches = str.split(str.strip(request.GET.get('branches', []))[:-1], '|')
            marks = str.split(str.strip(request.GET.get('marks', [])), '|')

            min_marks = str.split(marks[0], ',')
            sslc_min = Decimal(min_marks[0])
            puc_min = Decimal(min_marks[1])
            cgpa_min = Decimal(min_marks[2])
            max_marks = str.split(marks[1], ',')
            sslc_max = Decimal(max_marks[0])
            puc_max = Decimal(max_marks[1])
            cgpa_max = Decimal(max_marks[2])

            if request.GET.get('get_inactive', False) == 'True':
                be_students = BE_Student_Marks.objects.filter(USN__department__in=branches, SSLC_percentage__gte=sslc_min, PUC_or_diploma_percentage__gte=puc_min, SSLC_percentage__lte=sslc_max, PUC_or_diploma_percentage__lte=puc_max, CGPA__gte=cgpa_min, CGPA__lte=cgpa_max)
                mca_students = MCA_Student_Marks.objects.filter(USN__department__in=branches, SSLC_percentage__gte=sslc_min, PUC_or_diploma_percentage__gte=puc_min, SSLC_percentage__lte=sslc_max, PUC_or_diploma_percentage__lte=puc_max, BCA_percentage__gte=puc_min, BCA_percentage__lte=puc_max, CGPA__gte=cgpa_min, CGPA__lte=cgpa_max)
                mba_students = MBA_Student_Marks.objects.filter(USN__department__in=branches, SSLC_percentage__gte=sslc_min, PUC_or_diploma_percentage__gte=puc_min, SSLC_percentage__lte=sslc_max, PUC_or_diploma_percentage__lte=puc_max, BBA_or_BCOM_percentage__gte=puc_min, BBA_or_BCOM_percentage__lte=puc_max, CGPA__gte=cgpa_min, CGPA__lte=cgpa_max)
            else:
                be_students = BE_Student_Marks.objects.filter(USN__status='active', USN__department__in=branches, SSLC_percentage__gte=sslc_min, PUC_or_diploma_percentage__gte=puc_min, SSLC_percentage__lte=sslc_max, PUC_or_diploma_percentage__lte=puc_max, CGPA__gte=cgpa_min, CGPA__lte=cgpa_max)
                mca_students = MCA_Student_Marks.objects.filter(USN__status='active', USN__department__in=branches, SSLC_percentage__gte=sslc_min, PUC_or_diploma_percentage__gte=puc_min, SSLC_percentage__lte=sslc_max, PUC_or_diploma_percentage__lte=puc_max, BCA_percentage__gte=puc_min, BCA_percentage__lte=puc_max, CGPA__gte=cgpa_min, CGPA__lte=cgpa_max)
                mba_students = MBA_Student_Marks.objects.filter(USN__status='active', USN__department__in=branches, SSLC_percentage__gte=sslc_min, PUC_or_diploma_percentage__gte=puc_min, SSLC_percentage__lte=sslc_max, PUC_or_diploma_percentage__lte=puc_max, BBA_or_BCOM_percentage__gte=puc_min, BBA_or_BCOM_percentage__lte=puc_max, CGPA__gte=cgpa_min, CGPA__lte=cgpa_max)

            ''' Download File else Return JSON Data'''
            if request.GET.get('download_detailed_list', False):
                book = get_student_details_file(
                    be_students, mca_students, mba_students, branches, True)
                response = HttpResponse(content_type='application/ms-excel')
                # force browser to download file
                response['Content-Disposition'] = 'attachment; filename=student_details.xls'
                book.save(response)
                return response
            if request.GET.get('download_attendance_list', False):
                book = get_student_details_file(
                    be_students, mca_students, mba_students, branches, False)
                response = HttpResponse(content_type='application/ms-excel')
                # force browser to download file
                response['Content-Disposition'] = 'attachment; filename=student_details.xls'
                book.save(response)
                return response
            else:
                data = get_json_data(be_students, mca_students, mba_students)
                return JsonResponse(data)
        else:
            return JsonResponse({'be_students': [], 'mca_students': [], 'mba_students': []})


def get_json_data(be_students, mca_students, mba_students):
    data = {'be_students': [], 'mca_students': [], 'mba_students': []}
    for student in be_students:
        temp = {
            'USN': student.USN.USN,
            'name': student.USN.name,
            'branch': student.USN.department,
            'email': student.USN.email,
            'phone': student.USN.phone,
            'sslc_percentage': student.SSLC_percentage,
            'puc_or_diploma': student.PUC_or_diploma,
            'puc_or_diploma_percentage': student.PUC_or_diploma_percentage,
            'cgpa': student.CGPA
        }
        data['be_students'].append(temp)
    for student in mca_students:
        temp = {
            'USN': student.USN.USN,
            'name': student.USN.name,
            'branch': student.USN.department,
            'email': student.USN.email,
            'phone': student.USN.phone,
            'sslc_percentage': student.SSLC_percentage,
            'puc_or_diploma': student.PUC_or_diploma,
            'puc_or_diploma_percentage': student.PUC_or_diploma_percentage,
            'bca_percentage': student.BCA_percentage,
            'cgpa': student.CGPA
        }
        data['mca_students'].append(temp)
    for student in mba_students:
        temp = {
            'USN': student.USN.USN,
            'name': student.USN.name,
            'branch': student.USN.department,
            'email': student.USN.email,
            'phone': student.USN.phone,
            'sslc_percentage': student.SSLC_percentage,
            'puc_or_diploma': student.PUC_or_diploma,
            'puc_or_diploma_percentage': student.PUC_or_diploma_percentage,
            'bba_or_bcom': student.BBA_or_BCOM,
            'finance_or_management': student.Finance_or_Management,
            'bba_or_bcom_percentage': student.BBA_or_BCOM_percentage,
            'cgpa': student.CGPA
        }
        data['mba_students'].append(temp)
    return data


def get_student_details_file(be_students, mca_students, mba_students, branches, detailed):
    book = xlwt.Workbook()
    font1 = xlwt.Font()
    font1.bold = True
    style1 = xlwt.XFStyle()
    style1.font = font1
    alignment = xlwt.Alignment()
    alignment.horz = xlwt.Alignment.HORZ_CENTER
    style1.alignment = alignment
    for branch in branches:
        sheet = book.add_sheet(branch)
        if detailed:
            if branch == 'MCA':
                sheet.write_merge(0, 0, 0, 11, branch, style1)
            elif branch == 'MBA':
                sheet.write_merge(0, 0, 0, 11, branch, style1)
            else:
                sheet.write_merge(0, 0, 0, 10, branch, style1)
        else:
            sheet.write_merge(0, 0, 0, 6, branch, style1)
        sheet.write(1, 0, 'Sl. No.', style1)
        sheet.write(1, 1, 'USN', style1)
        sheet.write(1, 2, 'Name', style1)
        sheet.write(1, 3, 'Branch', style1)
        sheet.write(1, 4, 'Email', style1)
        sheet.write(1, 5, 'Phone No.', style1)
        if detailed:
            sheet.write(1, 6, 'Date Of Birth', style1)
            sheet.write(1, 7, 'Gender', style1)
            sheet.write(1, 8, 'SSLC Percentage', style1)
            sheet.write(1, 9, '12th Percentage', style1)
            if branch == 'MCA':
                sheet.write(1, 10, 'BCA Percentage', style1)
                sheet.write(1, 11, 'CGPA', style1)
            elif branch == 'MBA':
                sheet.write(1, 10, 'BBA or Bcom Percentage', style1)
                sheet.write(1, 11, 'CGPA', style1)
            else:
                sheet.write(1, 10, 'CGPA', style1)
        else:
            sheet.write(1, 6, 'Signature', style1)
        if branch == 'MCA':
            Students_local = mca_students.filter(
                USN__department__icontains=branch)
        elif branch == 'MBA':
            Students_local = mba_students.filter(
                USN__department__icontains=branch)
        else:
            Students_local = be_students.filter(
                USN__department__icontains=branch)

        row = 2
        col = 0
        n = 0
        for student in Students_local:
            n += 1
            sheet.write(row, col, n)
            col += 1
            sheet.write(row, col, student.USN.USN)
            col += 1
            sheet.write(row, col, student.USN.name)
            col += 1
            sheet.write(row, col, student.USN.department)
            col += 1
            sheet.write(row, col, student.USN.email)
            col += 1
            sheet.write(row, col, str(student.USN.phone))
            col += 1
            if detailed:
                try:
                    d = str(student.USN.date_of_birth.strftime('%d-%m-%Y'))
                except:
                    d = 'Not Entered'
                sheet.write(row, col, d)
                col += 1
                sheet.write(row, col, student.USN.gender)
                col += 1
                sheet.write(row, col, student.SSLC_percentage)
                col += 1
                sheet.write(row, col, student.PUC_or_diploma_percentage)
                col += 1
                if branch == 'MCA':
                    sheet.write(row, col, student.BCA_percentage)
                    col += 1
                if branch == 'MBA':
                    sheet.write(row, col, student.BBA_or_BCOM_percentage)
                    col += 1
                sheet.write(row, col, student.CGPA)
            else:
                sheet.write(row, col, '')
            row += 1
            col = 0
    return book


def register(request):
    permission = User_Permissions.objects.all()[0]
    if not permission.registration_open:
        return redirect('/users/log-in/')
    if request.method == 'POST':
        USN = request.POST['USN']
        if Student.objects.filter(USN=USN).exists():
            messages.info(request, 'USN already registered')
            return render(request, 'add_student_form.html')
        name = request.POST['name']
        department = request.POST['department']
        email = request.POST['email']
        phone = request.POST['phone']
        date_of_birth = datetime.datetime.strptime(request.POST['date_of_birth'], '%Y-%m-%d')
        gender = request.POST['gender']
        if department in ['ISE', 'CSE', 'MEC', 'ECE', 'CIV']:
            try:
                sslc = Decimal(request.POST['be_sslc_percentage'])
                puc_or_diploma = request.POST['be_puc_or_diploma']
                puc_or_diploma_percentage = Decimal(request.POST['be_puc_or_diploma_percentage'])
                cgpa = Decimal(request.POST['be_cgpa'])
                student = Student(USN=USN, name=name, department=department, email=email, phone=phone, date_of_birth=date_of_birth, gender=gender, last_edited_by=USN)
                student.save()
            except:
                messages.info(request, 'Registration Unsuccessful')
                return render(request, 'add_student_form.html')
            try:
                be_student = BE_Student_Marks(USN=student, SSLC_percentage=sslc, PUC_or_diploma=puc_or_diploma, PUC_or_diploma_percentage=puc_or_diploma_percentage, CGPA=cgpa)
                be_student.save()
            except:
                student.delete()
                messages.info(request, 'Registration Unsuccessful')
                return render(request, 'add_student_form.html')
        if department == 'MCA':
            try:
                sslc = Decimal(request.POST['mca_sslc_percentage'])
                puc_or_diploma = request.POST['mca_puc_or_diploma']
                puc_or_diploma_percentage = Decimal(request.POST['mca_puc_or_diploma_percentage'])
                bca = Decimal(request.POST['bca_percentage'])
                cgpa = Decimal(request.POST['mca_cgpa'])
                student = Student(USN=USN, name=name, department=department, email=email, phone=phone, date_of_birth=date_of_birth, gender=gender, last_edited_by=USN)
                student.save()
            except:
                messages.info(request, 'Registration Unsuccessful')
                return render(request, 'add_student_form.html')
            try:
                mca_student = MCA_Student_Marks(USN=student, SSLC_percentage=sslc, PUC_or_diploma=puc_or_diploma, PUC_or_diploma_percentage=puc_or_diploma_percentage, BCA_percentage=bca, CGPA=cgpa)
                mca_student.save()
            except:
                student.delete()
                messages.info(request, 'Registration Unsuccessful')
                return render(request, 'add_student_form.html')
        if department == 'MBA':
            try:
                sslc = Decimal(request.POST['mba_sslc_percentage'])
                puc_or_diploma = request.POST['mba_puc_or_diploma']
                puc_or_diploma_percentage = Decimal(request.POST['mba_puc_or_diploma_percentage'])
                bba_or_bcom = request.POST['bba_or_bcom']
                finance_or_management = request.POST['finance_or_management']
                bba_or_bcom_percentage = Decimal(request.POST['bba_or_bcom_percentage'])
                cgpa = Decimal(request.POST['mba_cgpa'])
                student = Student(USN=USN, name=name, department=department, email=email, phone=phone, date_of_birth=date_of_birth, gender=gender, last_edited_by=USN)
                student.save()
            except:
                messages.info(request, 'Registration Unsuccessful')
                return render(request, 'add_student_form.html')
            try:
                mba_student = MBA_Student_Marks(USN=student, SSLC_percentage=sslc, PUC_or_diploma=puc_or_diploma, PUC_or_diploma_percentage=puc_or_diploma_percentage, BBA_or_BCOM=bba_or_bcom, Finance_or_Management=finance_or_management, BBA_or_BCOM_percentage=bba_or_bcom_percentage, CGPA=cgpa)
                mba_student.save()
            except:
                student.delete()
                messages.info(request, 'Registration Unsuccessful')
                return render(request, 'add_student_form.html')
        return redirect('/users/log-in/')
    return render(request, 'add_student_form.html')


def add_students(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        z = 1
        uploaded_file = request.FILES['student_file']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        # try:
        path = os.path.join(settings.BASE_DIR, 'media')
        book = xlrd.open_workbook(path+'/'+name)
        sheet = book.sheet_by_index(0)
        nrows = sheet.nrows

        col = 1
        for row in range(1, nrows):
            email = sheet.cell_value(row, col)
            col += 1
            usn = sheet.cell_value(row, col)
            col += 1
            name = sheet.cell_value(row, col)
            col += 1
            branch = sheet.cell_value(row, col)
            col += 1
            phone = str(sheet.cell_value(row, col))
            if phone.endswith('.0'):
                phone = phone[0:-2]
            col += 1
            try:
                a1 = sheet.cell_value(row, col)
                x = datetime.datetime(*xlrd.xldate_as_tuple(a1, book.datemode))
                dob = x
            except:
                a1 = datetime.datetime(int(str(sheet.cell_value(row, col))[6:]), int(
                    str(sheet.cell_value(row, col))[3:5]), int(str(sheet.cell_value(row, col))[0:2]))
                dob = a1
            col += 1
            gender = sheet.cell_value(row, col)
            col += 1
            sslc = Decimal(sheet.cell_value(row, col))
            col += 1
            puc = Decimal(sheet.cell_value(row, col))
            puc_diploma = 'PUC'
            col += 1
            cgpa = Decimal(sheet.cell_value(row, col))
            col = 1
            if not Student.objects.filter(USN=usn).exists():
                student = Student(USN=usn, name=name, department=branch,
                                  email=email, phone=phone, date_of_birth=dob, gender=gender, last_edited_by='Added')
                student.save()
                be_student = BE_Student_Marks(
                    USN=student, SSLC_percentage=sslc, PUC_or_diploma=puc_diploma, PUC_or_diploma_percentage=puc, CGPA=cgpa)
                be_student.save()
            else:
                student = Student.objects.filter(USN=usn)
                student.delete()
                student = Student(USN=usn, name=name, department=branch, email=email, phone=phone, date_of_birth=dob, gender=gender, last_edited_by='Added')
                student.save()
                be_student = BE_Student_Marks(USN=student, SSLC_percentage=sslc, PUC_or_diploma=puc_diploma, PUC_or_diploma_percentage=puc, CGPA=cgpa)
                be_student.save()
                # print(z,':',usn)
                z += 1
        # except:
        #    print('hi')

        fs1 = FileSystemStorage()
        fs1.delete(uploaded_file.name)
        return redirect('/student/')
    return redirect('/users/log-in/')


def edit_student(request):
    permission = User_Permissions.objects.all()[0]
    if request.session.has_key('user') or request.session.has_key('student'):
        if request.session.has_key('user'):
            username = request.session['user']
            user = User.objects.get(user_id=username)
            if user.is_admin() or (user.is_coordinator() and permission.coordinator_edit_student_details):
                if request.method == 'GET' and request.GET.get('usn', False):
                    usn = request.GET['usn']
                    student = Student.objects.get(USN=usn)
                    if student.department == 'MCA':
                        student = MCA_Student_Marks.objects.get(USN=student)
                    elif student.department == 'MBA':
                        student = MBA_Student_Marks.objects.get(USN=student)
                    else:
                        student = BE_Student_Marks.objects.get(USN=student)
                    return render(request, 'edit_student.html', {'student': student, 'user': user})
                if request.method == 'POST':
                    return edit_student_details(request, user.name, False)
        elif request.session.has_key('student'):
            usn = request.session['student']
            student = Student.objects.get(USN=usn)
            if permission.students_edit_their_details:
                if request.method == 'GET' and request.GET.get('usn', False):
                    usn = request.GET['usn']
                    student = Student.objects.get(USN=usn)
                    if student.department == 'MCA':
                        student = MCA_Student_Marks.objects.get(USN=student)
                    elif student.department == 'MBA':
                        student = MBA_Student_Marks.objects.get(USN=student)
                    else:
                        student = BE_Student_Marks.objects.get(USN=student)
                    return render(request, 'edit_student.html', {'student': student})
                if request.method == 'POST':
                    return edit_student_details(request, student.USN, True)
    return redirect('/users/log-in')

def edit_student_details(request, editor_name, is_student):
    USN = request.POST['USN']
    student = Student.objects.get(USN=USN)
    student.name = request.POST['name']

    student.email = request.POST['email']
    student.phone = request.POST['phone']
    student.date_of_birth = datetime.datetime.strptime(
        request.POST['date_of_birth'], '%Y-%m-%d')
    student.gender = request.POST['gender']
    student.status = request.POST['status']
    student.last_edited_by = editor_name
    if student.department in ['ISE', 'CSE', 'MEC', 'ECE', 'CIV']:
        try:
            student.save()
            be_student = BE_Student_Marks.objects.get(USN=student)
            be_student.SSLC_percentage = Decimal(
                request.POST['be_sslc_percentage'])
            be_student.PUC_or_diploma = request.POST['be_puc_or_diploma']
            be_student.PUC_or_diploma_percentage = Decimal(
                request.POST['be_puc_or_diploma_percentage'])
            be_student.CGPA = Decimal(request.POST['be_cgpa'])
            be_student.save()
        except:
            messages.info(request, 'Edit Unsuccessful')
            return render(request, 'edit_student.html', {'student': be_student, 'user': user})
    if student.department == 'MCA':
        try:
            student.save()
            mca_student = MCA_Student_Marks.objects.get(USN=student)
            mca_student.SSLC_percentage = Decimal(
                request.POST['mca_sslc_percentage'])
            mca_student.PUC_or_diploma = request.POST['mca_puc_or_diploma']
            mca_student.PUC_or_diploma_percentage = Decimal(
                request.POST['mca_puc_or_diploma_percentage'])
            mca_student.BCA_percentage = Decimal(
                request.POST['bca_percentage'])
            mca_student.CGPA = Decimal(request.POST['mca_cgpa'])
            mca_student.save()
        except:
            messages.info(request, 'Edit Unsuccessful')
            return render(request, 'edit_student.html', {'student': mca_student, 'user': user})
    if student.department == 'MBA':
        try:
            student.save()
            mba_student = MBA_Student_Marks.objects.get(USN=student)
            mba_student.SSLC_percentage = Decimal(
                request.POST['mba_sslc_percentage'])
            mba_student.PUC_or_diploma = request.POST['mba_puc_or_diploma']
            mba_student.PUC_or_diploma_percentage = Decimal(
                request.POST['mba_puc_or_diploma_percentage'])
            mba_student.BBA_or_BCOM = request.POST['bba_or_bcom']
            mba_student.Finance_or_Management = request.POST['finance_or_management']
            mba_student.BBA_or_BCOM_percentage = Decimal(
                request.POST['bba_or_bcom_percentage'])
            mba_student.CGPA = Decimal(request.POST['mba_cgpa'])
            mba_student.save()
        except:
            messages.info(request, 'Edit Unsuccessful')
            return render(request, 'edit_student.html', {'student': mba_student, 'user': user})
    if not is_student:
        return redirect('/student/')
    if is_student:
        return redirect('/student/home/')

def student_summary(request):
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
        if request.GET.get('usn', False) and request.GET.get('branch', False):
            usn = request.GET['usn']
            branch = request.GET['branch']

            ''' Student Details '''
            if branch.upper() in ['ISE', 'CSE', 'ECE', 'MEC', 'CIV']:
                student = BE_Student_Marks.objects.get(USN__USN=usn)
            if branch.upper() == 'MBA':
                student = MBA_Student_Marks.objects.get(USN__USN=usn)
            if branch.upper() == 'MCA':
                student = MCA_Student_Marks.objects.get(USN__USN=usn)

            student.eligible = len(
                Student_Company_Registration.objects.filter(student__USN=usn))
            student.attended = len(Student_Company_Registration.objects.filter(
                student__USN=usn, status='Registered'))
            student.placed = len(Student_Placed.objects.filter(USN=usn))

            ''' Company Details '''
            companies = Student_Company_Registration.objects.filter(
                student__USN=usn)
            companies_list = []
            for company in companies:
                rounds = Company_Round.objects.filter(
                    company__id=company.company.id)
                temp = []
                next_round = True
                reg = False
                for round in rounds:
                    if round.status in ['2', '0']:
                        date = round.round_date
                        if company.status == 'Registered':
                            round_name = round.round_title
                            if next_round:
                                status = Student_Company_Round.objects.get(
                                    company_round=round, student__USN=usn).status
                            temp.append({'title': round.round_title, 'date': round.round_date, 'header_title': round_name, 'status': ': '+status+' |', 'next_round': next_round})
                            if status != 'Pass':
                                next_round = False
                            reg = True
                        else:
                            round_name = ''
                            status = company.status
                            temp.append({'title': round.round_title, 'date': round.round_date, 'header_title': round_name, 'status': status, 'next_round': next_round})
                            next_round = False
                    else:
                        round_name = ''
                        if not reg:
                            status = company.status
                        else:
                            status = ''
                        temp.append({'title': round.round_title, 'date': round.round_date, 'header_title': round_name, 'status': status, 'next_round': next_round})
                        next_round = False

                companies_list.append(
                    {'company': company.company, 'rounds': temp})

            ''' Student Stats '''
            stats = {}

            aptitude = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
            aptitude['attended'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Aptitude', status__in=['Pass', 'Fail']))
            aptitude['cleared'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Aptitude', status='Pass'))
            if aptitude['attended'] != 0:
                aptitude['pass_percentage'] = (
                    aptitude['cleared']/aptitude['attended'])
            else:
                aptitude['pass_percentage'] = 0
            stats['aptitude'] = aptitude

            discussion = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
            discussion['attended'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Discussion', status__in=['Pass', 'Fail']))
            discussion['cleared'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Discussion', status='Pass'))
            if discussion['attended'] != 0:
                discussion['pass_percentage'] = (discussion['cleared']/discussion['attended'])
            else:
                discussion['pass_percentage'] = 0
            stats['discussion'] = discussion

            technical = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
            technical['attended'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Technical', status__in=['Pass', 'Fail']))
            technical['cleared'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Technical', status='Pass'))
            if technical['attended'] != 0:
                technical['pass_percentage'] = (technical['cleared']/technical['attended'])
            else:
                technical['pass_percentage'] = 0
            stats['technical'] = technical

            interview = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
            interview['attended'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Interview'))
            interview['cleared'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Interview', status='Pass'))
            if interview['attended'] != 0:
                interview['pass_percentage'] = (interview['cleared']/interview['attended'])
            else:
                interview['pass_percentage'] = 0
            stats['interview'] = interview

            return render(request, 'student_summary.html', {'student': student, 'user': user, 'permission': permission, 'companies': companies_list, 'stats': stats})
    return redirect('/users/log-in')


def student_home(request):
    if request.session.has_key('student'):
        permission = User_Permissions.objects.all()[0]
        usn = request.session['student']
        student_local = Student.objects.get(USN=usn)
        if student_local.department in ['ISE', 'CSE', 'ECE', 'MEC', 'CIV']:
            student = BE_Student_Marks.objects.get(USN__USN=usn)
        if student_local.department == 'MBA':
            student = MBA_Student_Marks.objects.get(USN__USN=usn)
        if student_local.department == 'MCA':
            student = MCA_Student_Marks.objects.get(USN__USN=usn)

        student.eligible = len(
            Student_Company_Registration.objects.filter(student__USN=usn))
        student.attended = len(Student_Company_Registration.objects.filter(
            student__USN=usn, status='Registered'))
        student.placed = len(Student_Placed.objects.filter(USN=usn))

        ''' Company Details '''
        companies_name = Student_Placed.objects.filter(USN=student.USN)
        companies = []
        for company_name in companies_name:
            companies.append(Company.objects.get(
                company_name=company_name.company))
        #companies = Student_Company_Registration.objects.filter(student__USN=usn, company__status__in=['2','1'])
        companies_list = []
        for company in companies:
            rounds = Company_Round.objects.filter(company__id=company.id)
            temp = []
            next_round = True
            reg = False
            for round in rounds:
                if round.status in ['2', '0']:
                    date = round.round_date
                    if company.status == 'Registered':
                        round_name = round.round_title
                        if next_round:
                            status = Student_Company_Round.objects.get(company_round=round, student__USN=usn).status
                        temp.append({'title': round.round_title, 'date': round.round_date, 'header_title': round_name, 'status': ': '+status+' |', 'next_round': next_round})
                        if status != 'Pass':
                            next_round = False
                        reg = True
                    else:
                        round_name = ''
                        status = company.status
                        temp.append({'title': round.round_title, 'date': round.round_date, 'header_title': round_name, 'status': status, 'next_round': next_round})
                        next_round = False
                else:
                    round_name = ''
                    if not reg:
                        status = company.status
                    else:
                        status = ''
                    temp.append({'title': round.round_title, 'date': round.round_date, 'header_title': round_name, 'status': status, 'next_round': next_round})
                    next_round = False

            companies_list.append({'company': company, 'rounds': temp})

        ''' Student Stats '''
        stats = {}

        aptitude = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
        aptitude['attended'] = len(Student_Company_Round.objects.filter(
            student__USN=usn, company_round__round_type='Aptitude', status__in=['Pass', 'Fail']))
        aptitude['cleared'] = len(Student_Company_Round.objects.filter(
            student__USN=usn, company_round__round_type='Aptitude', status='Pass'))
        if aptitude['attended'] != 0:
            aptitude['pass_percentage'] = (aptitude['cleared']/aptitude['attended'])
        else:
            aptitude['pass_percentage'] = 0
        stats['aptitude'] = aptitude

        discussion = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
        discussion['attended'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Discussion', status__in=['Pass', 'Fail']))
        discussion['cleared'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Discussion', status='Pass'))
        if discussion['attended'] != 0:
            discussion['pass_percentage'] = (
                discussion['cleared']/discussion['attended'])
        else:
            discussion['pass_percentage'] = 0
        stats['discussion'] = discussion

        technical = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
        technical['attended'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Technical', status__in=['Pass', 'Fail']))
        technical['cleared'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Technical', status='Pass'))
        if technical['attended'] != 0:
            technical['pass_percentage'] = (technical['cleared']/technical['attended'])
        else:
            technical['pass_percentage'] = 0
        stats['technical'] = technical

        interview = {'attended': 0, 'pass': 0, 'pass_percentage': 0}
        interview['attended'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Interview'))
        interview['cleared'] = len(Student_Company_Round.objects.filter(student__USN=usn, company_round__round_type='Interview', status='Pass'))
        if interview['attended'] != 0:
            interview['pass_percentage'] = (interview['cleared']/interview['attended'])
        else:
            interview['pass_percentage'] = 0
        stats['interview'] = interview

        return render(request, 'student_home.html', {'home': True, 'student': student, 'permission': permission, 'companies': companies_list, 'stats': stats})
    else:
        return redirect('/users/log-in/')


def student_companies(request):
    permission = User_Permissions.objects.all()[0]
    if request.session.has_key('student'):
        usn = request.session['student']
        student_local = Student.objects.get(USN=usn)
        if student_local.department in ['ISE', 'CSE', 'ECE', 'MEC', 'CIV']:
            student = BE_Student_Marks.objects.get(USN__USN=usn)
        if student_local.department == 'MBA':
            student = MBA_Student_Marks.objects.get(USN__USN=usn)
        if student_local.department == 'MCA':
            student = MCA_Student_Marks.objects.get(USN__USN=usn)
            
        ''' Company Details '''
        companies = Student_Company_Registration.objects.filter(student__USN=student.USN).order_by('company__status')
        companies_list = []
        for company in companies:
            rounds = Company_Round.objects.filter(company__id=company.company.id)
            temp = []
            next_round = True
            reg = False
            for round in rounds:
                if round.status in ['2', '0']:
                    date = round.round_date
                    if company.status == 'Registered':
                        round_name = round.round_title
                        if next_round:
                            status = Student_Company_Round.objects.get(company_round=round, student__USN=usn).status
                        temp.append({'title': round.round_title, 'date': round.round_date, 'header_title': round_name, 'status': ': '+status+' |', 'next_round': next_round})
                        if status != 'Pass':
                            next_round = False
                        reg = True
                    else:
                        round_name = ''
                        status = company.status
                        temp.append({'title': round.round_title, 'date': round.round_date,
                                     'header_title': round_name, 'status': status, 'next_round': next_round})
                        next_round = False
                else:
                    round_name = ''
                    if not reg:
                        status = company.status
                    else:
                        status = ''
                    temp.append({'title': round.round_title, 'date': round.round_date,
                                 'header_title': round_name, 'status': status, 'next_round': next_round})
                    next_round = False
            registeration = Company_Registration_Time.objects.get(company__id=company.company.id)
            companies_list.append({'company': company.company, 'rounds': temp, 'registration': registeration})
        return render(request, 'student_companies.html', {'student': student, 'company': True, 'permission': permission, 'companies': companies_list})
    else:
        return redirect('/users/log-in/')

def register_to_company(request):
    if request.session.has_key('student'):
        usn = request.session['student']
        student = Student.objects.get(USN=usn)
        if request.GET.get('company', False) and request.GET.get('status', False):
            company_id = request.GET.get('company', False)
            status = request.GET.get('status', False)
            student_reg = Student_Company_Registration.objects.get(student=student, company__id=company_id)
            student_reg.status = status
            student_reg.save()
            student_reg = Student_Company_Registration.objects.get(student=student, company__id=company_id)
            return HttpResponse(student_reg.status)
    else:
        return redirect('/users/log-in/')

def student_change_password(request):
    if request.session.has_key('student'):
        usn = request.session['student']
        try:
            student = Student.objects.get(USN=usn)
        except:
            return redirect('/users/log-in')
    if not (request.session.has_key('student')):
        return redirect('/users/log-in')
    if request.method == 'POST':
        old_password = request.POST['old_password']
        new_password = request.POST['new_password']
        if student.password == old_password:
            student.password = new_password
            student.save()
            messages.info(request, 'Password Changed Successfully')
        else:
            messages.info(request, 'Incorrect Current Password')
        return redirect('/student/home/')