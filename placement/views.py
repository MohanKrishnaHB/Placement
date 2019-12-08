from django.shortcuts import render, redirect
from activity.models import Student_Company_Round, Student_Placed, Student_Company_Registration
from company.models import Company
from user.models import User, User_Permissions

def home_page(request):
    try:
        permission = User_Permissions.objects.all()[0]
    except:
        permission = User_Permissions()
        permission.save()
        
    if request.session.has_key('student'):
        return redirect('/student/home/')
    if request.session.has_key('user'):
        username = request.session['user']
        try:
            user = User.objects.get(user_id=username)
        except:
            return redirect('/users/log-in')
        
        branches = ['ISE', 'CSE', 'ECE', 'MEC', 'CIV', 'MCA', 'MBA']
        if user.department != 'Placement' and user.department != 'other':
            branches = [user.department]
        ''' Stats '''
        stats = {'aptitude_pass_percentage': 0, 'discussion_pass_percentage': 0, 'technical_pass_percentage': 0, 'interview_pass_percentage': 0}
        apti_attended = len(Student_Company_Round.objects.filter(company_round__round_type='Aptitude', status__in=['Pass', 'Fail'], student__department__in=branches))
        apti_cleared = len(Student_Company_Round.objects.filter(company_round__round_type='Aptitude', status='Pass', student__department__in=branches))
        try:
            stats['aptitude_pass_percentage'] = apti_cleared/apti_attended
        except:
            stats['aptitude_pass_percentage'] = 0
        
        gd_attended = len(Student_Company_Round.objects.filter(company_round__round_type='Discussion', status__in=['Pass', 'Fail']))
        gd_cleared = len(Student_Company_Round.objects.filter(company_round__round_type='Discussion', status='Pass'))
        try:
            stats['discussion_pass_percentage'] = gd_cleared/gd_attended
        except:
            stats['discussion_pass_percentage'] = 0
        
        tech_attended = len(Student_Company_Round.objects.filter(company_round__round_type='Technical', status__in=['Pass', 'Fail']))
        tech_cleared = len(Student_Company_Round.objects.filter(company_round__round_type='Technical', status='Pass'))
        try:
            stats['technical_pass_percentage'] = tech_cleared/tech_attended
        except:
            stats['technical_pass_percentage'] = 0
        
        hr_attended = len(Student_Company_Round.objects.filter(company_round__round_type='Interview', status__in=['Pass', 'Fail']))
        hr_cleared = len(Student_Company_Round.objects.filter(company_round__round_type='Interview', status='Pass'))
        try:
            stats['interview_pass_percentage'] = hr_cleared/hr_attended
        except:
            stats['interview_pass_percentage'] = 0
        
        ''' Company Details '''
        companies = Company.objects.filter(status='1')
        for company in companies:
            company.registered = len(Student_Company_Registration.objects.filter(company=company, status='Registered'))
            company.placed = len(Student_Placed.objects.filter(company=company.company_name))
        
        return render(request, 'home_page.html', {'user': user, 'stats': stats, 'companies': companies})
    else:
        return redirect('/users/log-in')