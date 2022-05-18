from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from common.models import MyUser
from leave.models import LevHistory
from ..models import CmtHistory
from django.core.paginator import Paginator
import datetime
from django.db.models import Q
from operator import itemgetter


@login_required(login_url='common:login')
def history(request):
    # 로그인한 계정의 출퇴근 내역 가져오기
    myuser = get_object_or_404(MyUser, email=request.user.email)
    mylist = CmtHistory.objects.filter(employee=myuser).order_by('-startdatetime')

    today_week = datetime.datetime.now().isocalendar()[1]
    this_week_cmtlist = CmtHistory.objects.filter(employee=myuser, weeknum=today_week).order_by('-startdatetime')
    sum_workinghours = 0
    sum_overtime = 0
    for i in this_week_cmtlist:
        sum_workinghours = sum_workinghours + i.workinghours
        sum_overtime = sum_overtime + i.overtime

    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    dt = request.GET.get('dt', '') # 검색일자
    ct = request.GET.get('ct', '') # 검색구분
    kw = request.GET.get('kw', 0)  # 오버타임

    if dt != '' and  ct != '':
        mylist = mylist.filter(overtime__gte=kw, todaycat__icontains=ct, startdatetime__gte=dt).distinct()
    elif dt == '' and ct != '':
        mylist = mylist.filter(overtime__gte=kw, todaycat__icontains=ct).distinct()
    elif dt != '' and ct == '':
        mylist = mylist.filter(overtime__gte=kw, startdatetime__gte=dt).distinct()
    else:
        mylist = mylist.filter(overtime__gte=kw).distinct()
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    context = {'myuser':myuser, 'mylist': page_obj, 'page': page, 'kw': kw, 'dt':dt, 'ct': ct, 'sum_workinghours':round(sum_workinghours, 1), 'sum_overtime':round(sum_overtime, 1)}
    return render(request, 'commute/commute_hist.html', context)


@login_required(login_url='common:login')
def situation(request):

    try:
        myuser = get_object_or_404(MyUser, email=request.user.email)
    except Exception as e:
        myuser = ''
        print(f"Exceiption occured:\n{e}")

    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.time(0, 0, 0))
    today_end = datetime.datetime.combine(today, datetime.time(23, 59 ,59))
    commuters = CmtHistory.objects.filter(startdatetime__gte=today_start, startdatetime__lte=today_end).order_by('startdatetime', 'enddatetime')
    commuting_list = []
    for i in commuters:
        commuting_list.append(i.employee.realname)
    mgr_or_admin = MyUser.objects.filter(Q(is_admin=True) | Q(is_manager=True))
    for i in mgr_or_admin:
        commuting_list.append(i.realname)
    noncommute_users = MyUser.objects.filter().exclude(realname__in=commuting_list).order_by('realname')
    today_leave_list = LevHistory.objects.filter(startdate__lte=today, enddate__gte=today, approval='3').order_by('startdate')
    leave_dict = {'AL':'연차', 'MO':'오전 반차', 'AO':'오후 반차', 'CV':'경조 휴가', 'OL':'공가', 'EL':'조퇴', 'AB':'결근', 'SL':'병가'}
    noncommuters = []
    for i in noncommute_users:
        todaycat = '평일'
        for j in today_leave_list:
            if str(j.employee_id) == str(i.id):
                todaycat = leave_dict.get(str(j.leavecat))
        noncommuters.append({'todaycat':todaycat, 'openingtime':i.openingtime, 'realname':i.realname})
    noncommuters = sorted(noncommuters, key=itemgetter('todaycat', 'openingtime', 'realname'))
     
    context = {'myuser':myuser, 'commuters': commuters, 'noncommuters': noncommuters}
    return render(request, 'commute/commute_situ.html', context)


@login_required(login_url='common:login')
def totalhistory(request):
    try:
        myuser = get_object_or_404(MyUser, email=request.user.email)
    except Exception as e:
        myuser = ''
        print(f"Exceiption occured:\n{e}")

    # 전체 출근내역 가져오기
    mylist = CmtHistory.objects.filter().order_by('-startdatetime')

    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    dt = request.GET.get('dt', '') # 검색일자
    ct = request.GET.get('ct', '') # 검색구분
    kw = request.GET.get('kw', 0)  # 오버타임

    if dt != '' and  ct != '':
        mylist = mylist.filter(overtime__gte=kw, todaycat__icontains=ct, startdatetime__gte=dt).distinct()
    elif dt == '' and ct != '':
        mylist = mylist.filter(overtime__gte=kw, todaycat__icontains=ct).distinct()
    elif dt != '' and ct == '':
        mylist = mylist.filter(overtime__gte=kw, startdatetime__gte=dt).distinct()
    else:
        mylist = mylist.filter(overtime__gte=kw).distinct()
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    context = {'myuser':myuser, 'email': request.user.email, 'mylist': page_obj, 'page': page, 'kw': kw, 'dt': dt, 'ct': ct}
    return render(request, 'commute/commute_toth.html', context)