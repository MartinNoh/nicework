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
    kw = request.GET.get('kw', '')  # 검색어

    TODAYCAT_CHOICES = (('AL', '연차'), ('MO', '오전반차'), ('AO', '오후반차')
        , ('CV', '경조휴가'), ('OL', '공가'), ('EL', '조퇴'), ('AB', '결근'), ('SL', '병가')
        , ('HD', '공휴일'), ('WE', '주말'), ('WD', '평일'))
    todaycat_reverse = dict((v, k) for k, v in TODAYCAT_CHOICES)
    
    if kw:
        try:
            mylist = mylist.filter(
                Q(startdatetime__icontains=kw) |
                Q(todaycat__icontains=todaycat_reverse[kw.replace(' ', '')])
            ).distinct()
        except Exception as e:
            mylist = mylist.filter(
                Q(startdatetime__icontains=kw)
            ).distinct()
            print(f"Exceiption occured:\n{e}")
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    context = {'myuser':myuser, 'mylist': page_obj, 'page': page, 'kw': kw, 'sum_workinghours':round(sum_workinghours, 1), 'sum_overtime':round(sum_overtime, 1)}
    return render(request, 'commute/commute_hist.html', context)


@login_required(login_url='common:login')
def situation(request):
    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.time(0, 0, 0))
    today_end = datetime.datetime.combine(today, datetime.time(23, 59 ,59))
    commuters = CmtHistory.objects.filter(startdatetime__gte=today_start, startdatetime__lte=today_end).order_by('startdatetime', 'enddatetime')
    commuting_list = []
    for i in commuters:
        commuting_list.append(i.employee.realname)
    mgr_or_admin = MyUser.objects.filter(Q(is_admin=True) | Q(is_mgr=True))
    for i in mgr_or_admin:
        commuting_list.append(i.realname)
    noncommute_users = MyUser.objects.filter().exclude(realname__in=commuting_list).order_by('realname')
    today_leave_list = LevHistory.objects.filter(startdate__lte=today, enddate__gte=today, approval='3').order_by('startdate')
    leave_dict = {'AL':'연차', 'MO':'오전 반차', 'AO':'오후 반차', 'CV':'경조 휴가', 'OL':'공가', 'EL':'조퇴', 'AB':'결근', 'SL':'병가'}
    noncommuters = []
    for i in noncommute_users:
        todaycat = '-'
        for j in today_leave_list:
            if str(j.employee_id) == str(i.id):
                todaycat = leave_dict.get(str(j.leavecat))
        noncommuters.append({'todaycat':todaycat, 'openingtime':i.openingtime, 'realname':i.realname})
    noncommuters = sorted(noncommuters, key=itemgetter('todaycat', 'openingtime', 'realname'))
     
    context = {'commuters': commuters, 'noncommuters': noncommuters}
    return render(request, 'commute/commute_situ.html', context)


@login_required(login_url='common:login')
def totalhistory(request):
    # 전체 출근내역 가져오기
    mylist = CmtHistory.objects.filter().order_by('-startdatetime')

    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')  # 검색어

    TODAYCAT_CHOICES = (('AL', '연차'), ('MO', '오전반차'), ('AO', '오후반차')
        , ('CV', '경조휴가'), ('OL', '공가'), ('EL', '조퇴'), ('AB', '결근'), ('SL', '병가')
        , ('HD', '공휴일'), ('WE', '주말'), ('WD', '평일'))
    todaycat_reverse = dict((v, k) for k, v in TODAYCAT_CHOICES)
    
    if kw:
        try:
            mylist = mylist.filter(
                Q(startdatetime__icontains=kw) |
                Q(todaycat__icontains=todaycat_reverse[kw.replace(' ', '')])
            ).distinct()
        except Exception as e:
            mylist = mylist.filter(
                Q(startdatetime__icontains=kw)
            ).distinct()
            print(f"Exception occrured:\n{e}")
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    context = {'email': request.user.email, 'mylist': page_obj, 'page': page, 'kw': kw}
    return render(request, 'commute/commute_toth.html', context)