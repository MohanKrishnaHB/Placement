from django.shortcuts import render, redirect, HttpResponse
from company.models import Company, Company_Round, Company_Department
from activity.models import Student_Company_Registration, Student_Company_Round, Student_Placed
from user.models import User, User_Permissions
import xlwt
# Create your views here.
def activity(request):
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
        if request.GET.get('company', False):
            branches = ['ISE', 'CSE', 'ECE', 'MEC', 'CIV', 'MBA', 'MCA']
            if user.department != 'Placement' and user.department != 'other':
                branches = [user.department]
            company_id = request.GET.get('company', False)
            company = Company.objects.get(id=company_id)
            elegible_students = Student_Company_Registration.objects.filter(company=company, student__department__in=branches)
            registered_count = len(elegible_students.filter(status='Registered'))
            rounds = Company_Round.objects.filter(company__id=company_id)
            students_rounds = []
            previous_round_id = 'registered'
            previous_round_status = '0';
            for round in rounds:
                students = Student_Company_Round.objects.filter(company_round=round, student__department__in=branches)
                pass_count = len(students.filter(status='Pass'))
                students_rounds.append({'round': round, 'students': students, 'passed_students_count': pass_count, 'previous_round_id': previous_round_id, 'previous_round_status': previous_round_status, 'last': False})
                previous_round_id = round.id
                previous_round_status = round.status
            students_rounds[-1]['last'] = True
            return render(request, 'activity.html', {'company': company, 'user': user, 'permission': permission, 'students_rounds': students_rounds, 'elegible_students': elegible_students, 'registered_count': registered_count})
        return redirect('/company/')
    return redirect('/users/log-in')

def change_student_status(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() or user.is_coordinator():
        if request.GET.get('usn', False) and request.GET.get('round', False) and request.GET.get('status', False):
            usn = request.GET.get('usn', False)
            round_id = request.GET.get('round', False)
            status = request.GET.get('status', False)
            if status in ['Not-Attended', 'Pass', 'Fail']:
                student_round_activity = Student_Company_Round.objects.get(company_round__id=round_id, student__USN=usn)
                old_status = student_round_activity.status
                if student_round_activity.company_round.status == '2':
                    student_round_activity.status = status
                    student_round_activity.save()
            student_round_activity = Student_Company_Round.objects.get(company_round__id=round_id, student__USN=usn)
            return HttpResponse(old_status)
    return redirect('/users/log-in')

def student_list(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin() or user.is_coordinator() or user.is_other():
        if request.GET.get('company', False) and request.GET.get('source', False):
            company_id = request.GET['company']
            branches = ['ISE', 'CSE', 'ECE', 'MEC', 'CIV', 'MBA', 'MCA']
            if user.department != 'Placement' and user.department != 'other':
                branches = [user.department]
            company = Company.objects.get(id=company_id)
            source = request.GET['source']
            company_branches = Company_Department.objects.filter(company=company)
            branches = []
            for branch in company_branches:
                branches.append(branch.department)
            if user.department != 'Placement' and user.department != 'other' and user.department in branches:
                branches = [user.department]
                
            ''' Get Appropriate students '''
            if source == 'eligible':
                title = company.company_name+' Eligible Students List'
                students = Student_Company_Registration.objects.filter(company__id=company_id)
            elif source == 'registered':
                title = company.company_name+' Registered Students List'
                students = Student_Company_Registration.objects.filter(company__id=company_id, status='Registered')
            else:
                round = Company_Round.objects.get(id=source)
                title = company.company_name+' : '+round.round_title+' round Passed Students List'
                students = Student_Company_Round.objects.filter(company_round__id=source, status='Pass')
            book = get_student_details_file(students, branches, title)
            response = HttpResponse(content_type='application/ms-excel')
            response['Content-Disposition'] = 'attachment; filename={}_{}.xls'.format(company.company_name, source)
            book.save(response)
            return response

def get_student_details_file(students, branches, title):
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
        sheet.write_merge(0, 0, 0, 5, title, style1)
        sheet.write_merge(1, 1, 0, 5, branch, style1)
        sheet.write(2, 0, 'Sl. No.', style1)
        sheet.write(2, 1, 'USN', style1)
        sheet.write(2, 2, 'Name', style1)
        sheet.write(2, 3, 'Branch', style1)
        sheet.write(2, 4, 'Email', style1)
        sheet.write(2, 5, 'Phone No.', style1)
        students_local_branch = students.filter(student__department=branch)
        row = 3
        col = 0
        n = 0
        for student in students_local_branch:
            n += 1
            sheet.write(row, col, n)
            col += 1
            sheet.write(row, col, student.student.USN)
            col += 1
            sheet.write(row, col, student.student.name)
            col += 1
            sheet.write(row, col, student.student.department)
            col += 1
            sheet.write(row, col, student.student.email)
            col += 1
            sheet.write(row, col, str(student.student.phone))
            col = 0
            row += 1
    return book

def register_all(request):
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
            students = Student_Company_Registration.objects.filter(company__id=company_id)
            for student in students:
                student.status = 'Registered'
                student.save()
            return redirect('/activity/?company='+company_id)
        return redirect('/company/')
    return redirect('/users/log-in')

def change_round_state(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    else:
        return redirect('/users/log-in')
    if user.is_admin():
        if request.GET.get('company', False) and request.GET.get('current_round', False) and request.GET.get('previous_round', False):
            company_id = request.GET.get('company', False)
            current_round_id = request.GET.get('current_round', False)
            previous_round_id = request.GET.get('previous_round', False)
            current_round = Company_Round.objects.get(id=current_round_id)
            if current_round.status == '1':
                if previous_round_id == 'registered':
                    students = Student_Company_Registration.objects.filter(company__id=company_id, status='Registered')
                    for student in students:
                        if not Student_Company_Round.objects.filter(student=student.student, company_round=current_round).exists():
                            student_round = Student_Company_Round(student=student.student, company_round=current_round, status='Fail')
                            student_round.save()
                else:
                    students = Student_Company_Round.objects.filter(company_round__id=previous_round_id, status='Pass')
                    for student in students:
                        if not Student_Company_Round.objects.filter(student=student.student, company_round=current_round).exists():
                            student_round = Student_Company_Round(student=student.student, company_round=current_round, status='Fail')
                            student_round.save()
                current_round.status = '2'
                current_round.save()
            elif current_round.status == '2':
                current_round.status = '0'
                current_round.save()
            return redirect('/activity/?company={}'.format(company_id))
    return redirect('/users/log-in')

def final_report(request):
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
    if not (request.session.has_key('user')):
        return redirect('/users/log-in')
    if user.is_admin():
        book = xlwt.Workbook()
        font1 = xlwt.Font()
        font1.bold = True
        style1 = xlwt.XFStyle()
        style1.font = font1
        alignment = xlwt.Alignment()
        alignment.horz = xlwt.Alignment.HORZ_CENTER
        style1.alignment = alignment
        sheet = book.add_sheet('Final_report')
        sheet.write_merge(0, 0, 0, 9, 'Final Report', style1)
        sheet.write(1, 0, 'Sl. No.', style1)
        sheet.write(1, 1, 'Company Name', style1)
        sheet.write(1, 2, 'Date Of Visit', style1)
        sheet.write(1, 3, 'Venue', style1)
        sheet.write(1, 4, 'Departments', style1)
        sheet.write(1, 5, 'Cut off(%)', style1)
        sheet.write(1, 6, 'Package', style1)
        sheet.write(1, 7, 'No. of Eligible Students', style1)
        sheet.write(1, 8, 'No. of Students Attended', style1)
        sheet.write(1, 9, 'No. of Students Placed', style1)
        row = 2
        col = 0
        n = 0
        companies = Company.objects.filter(status='1')
        for company in companies:
            students_registered = Student_Company_Registration.objects.filter(company=company)
            n += 1
            sheet.write(row, col, n)
            col += 1
            sheet.write(row, col, company.company_name)
            col += 1
            sheet.write(row, col, company.date_of_visit.strftime('%d-%m-%Y'))
            col += 1
            sheet.write(row, col, company.venue)
            col += 1
            branches = ''
            eligible_branches = Company_Department.objects.filter(company=company)
            for company_dept in eligible_branches:
                branches += ', '+company_dept.department

            sheet.write(row, col, branches)
            col += 1
            cutoff = '10th>='+str(company.min_SSLC_percentage)+'12th>='+str(company.min_PUC_percentage)+'BE>='+str(company.min_CGPA)
            sheet.write(row, col, cutoff)
            col += 1
            sheet.write(row, col, company.package)
            col += 1
            eligible_students = len(students_registered)
            sheet.write(row, col, eligible_students)
            col += 1
            registered = len(students_registered.filter(status='Registered'))
            sheet.write(row, col, registered)
            col += 1
            placed = len(Student_Placed.objects.filter(company=company.company_name))
            sheet.write(row, col, placed)
            row += 1
            col = 0
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=Final_Report.xls' # force browser to download file
        book.save(response)
        return response
    else:
        return redirect('/users/log-in')