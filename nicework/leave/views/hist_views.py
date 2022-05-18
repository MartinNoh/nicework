from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.models import MyUser
from commute.models import CmtHistory
from ..models import LevHistory
from django.core.paginator import Paginator
import datetime
from django.db.models import Q
from pytimekr import pytimekr


@login_required(login_url='common:login')
def history(request):
    # 로그인 계정으로 등록한 휴가 리스트 가져오기
    myuser = get_object_or_404(MyUser, email=request.user.email)
    mylist = LevHistory.objects.filter(employee=myuser).order_by('-created_at')
    
    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')  # 검색어
    LEAVECAT_CHOICES = (('AL', '연차'), ('MO', '오전반차'), ('AO', '오후반차')
        , ('CV', '경조휴가'), ('OL', '공가'), ('EL', '조퇴'), ('AB', '결근'), ('SL', '병가')
        , ('HD', '공휴일'), ('WE', '주말'), ('WD', '평일'))
    leavecat_reverse = dict((v, k) for k, v in LEAVECAT_CHOICES)
    
    if kw:
        try:
            mylist = mylist.filter(
                Q(reason__icontains=kw) |
                Q(leavecat__icontains=leavecat_reverse[kw.replace(' ', '')])
            ).distinct()
        except Exception as e:
            mylist = mylist.filter(
                Q(reason__icontains=kw)
            ).distinct()
            print(f"Exceiption occured:\n{e}")
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    # 한글 파일 다운로드 버튼 클릭
    if request.method == "POST":
        is_download = True
        r = get_leave_hwp(request.POST, myuser)
    else:
        is_download = False
        r = ''

    context = {'myuser': myuser, 'mylist': page_obj, 'page': page, 'kw': kw, 'source_html': r, 'is_download': is_download}
    return render(request, 'leave/leave_hist.html', context)


@login_required(login_url='common:login')
def delete(request, myreg_id):
    myuser = get_object_or_404(MyUser, email=request.user.email)
    leave = get_object_or_404(LevHistory, pk=myreg_id)
    # 관리자 또는 매니저인 경우
    if myuser.is_mgr | myuser.is_admin:
        pass
    else:
        if request.user != leave.employee:
            messages.error(request, '삭제권한이 없습니다')
            return redirect('leave:hist')
    leave.delete()
    return redirect('leave:hist')


@login_required(login_url='common:login')
def waiting(request):
    # 로그인 계정으로 등록한 휴가 리스트 가져오기
    myuser = get_object_or_404(MyUser, email=request.user.email)
    mylist = LevHistory.objects.filter(approval='1').order_by('-created_at')
    
    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')  # 검색어
    LEAVECAT_CHOICES = (('AL', '연차'), ('MO', '오전반차'), ('AO', '오후반차')
        , ('CV', '경조휴가'), ('OL', '공가'), ('EL', '조퇴'), ('AB', '결근'), ('SL', '병가')
        , ('HD', '공휴일'), ('WE', '주말'), ('WD', '평일'))
    leavecat_reverse = dict((v, k) for k, v in LEAVECAT_CHOICES)
    
    if kw:
        try:
            mylist = mylist.filter(
                Q(reason__icontains=kw) |
                Q(leavecat__icontains=leavecat_reverse[kw.replace(' ', '')])
            ).distinct()
        except Exception as e:
            mylist = mylist.filter(
                Q(reason__icontains=kw)
            ).distinct()
            print(f"Exceiption occured:\n{e}")
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    context = {'myuser': myuser, 'mylist': page_obj, 'page': page, 'kw': kw}
    return render(request, 'leave/leave_wait.html', context)


@login_required(login_url='common:login')
def approval(request):
    myuser = get_object_or_404(MyUser, email=request.user.email)
    myreg_id = request.GET.get('myreg_id')
    result = request.GET.get('result')
    leave = get_object_or_404(LevHistory, pk=myreg_id)
    # 관리자 또는 매니저인 경우
    if myuser.is_mgr or myuser.is_admin:
        if result == "ok":
            leave.approval = "3"
            leave.save()
            # 기존 출퇴근 내역 일자에 휴가 승인되면 todaycat 변경
            startdate = leave.startdate
            enddate = leave.enddate + datetime.timedelta(days=1)
            leaveuser = get_object_or_404(MyUser, email=leave.employee.email)
            commute_within_leave = CmtHistory.objects.filter(employee=leaveuser, startdatetime__gte=startdate, startdatetime__lt=enddate)
            for i in commute_within_leave:
                i.todaycat = str(leave.leavecat)
                i.save()
        elif result == "rtn":
            leave.approval = "2"
            leave.save()
        elif result == "bck":
            leave.approval = "1"
            leave.save()
            # 기존 출퇴근 내역 일자에 휴가 재고되면 todaycat 변경
            startdate = leave.startdate
            enddate = leave.enddate + datetime.timedelta(days=1)
            leaveuser = get_object_or_404(MyUser, email=leave.employee.email)

            # 휴일여부, 시업시간, 종업 시간
            today = datetime.date.today()
            today_weekday = today.weekday()
            holiday_list = pytimekr.holidays(datetime.datetime.now().year)
            if today in holiday_list:
                todaycat = "HD"
            elif today_weekday > 4:
                todaycat = "WE"
            else:
                todaycat = "WD"

            commute_within_leave = CmtHistory.objects.filter(employee=leaveuser, startdatetime__gte=startdate, startdatetime__lt=enddate)
            for i in commute_within_leave:
                i.todaycat = todaycat
                i.save()
    else:
        messages.error(request, '결재 권한이 없습니다')
    return redirect('leave:wait')


@login_required(login_url='common:login')
def totalhistory(request):
    # 로그인 계정으로 등록한 휴가 리스트 가져오기
    myuser = get_object_or_404(MyUser, email=request.user.email)
    mylist = LevHistory.objects.exclude(approval=1).order_by('-created_at')
    
    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    kw = request.GET.get('kw', '')  # 검색어
    LEAVECAT_CHOICES = (('AL', '연차'), ('MO', '오전반차'), ('AO', '오후반차')
        , ('CV', '경조휴가'), ('OL', '공가'), ('EL', '조퇴'), ('AB', '결근'), ('SL', '병가')
        , ('HD', '공휴일'), ('WE', '주말'), ('WD', '평일'))
    leavecat_reverse = dict((v, k) for k, v in LEAVECAT_CHOICES)
    
    if kw:
        try:
            mylist = mylist.filter(
                Q(reason__icontains=kw) |
                Q(leavecat__icontains=leavecat_reverse[kw.replace(' ', '')])
            ).distinct()
        except Exception as e:
            mylist = mylist.filter(
                Q(reason__icontains=kw)
            ).distinct()
            print(f"Exceiption occured:\n{e}")
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    context = {'myuser': myuser, 'mylist': page_obj, 'page': page, 'kw': kw}
    return render(request, 'leave/leave_toth.html', context)


def get_leave_hwp(data, myuser):
    opening_time = myuser.openingtime
    closing_time = myuser.closingtime
    time_diff = datetime.datetime.combine(datetime.date.today(), closing_time) - datetime.datetime.combine(datetime.date.today(), opening_time)
    t_diff = time_diff.days*24 + time_diff.seconds/3600
    if t_diff >= 8:
        breaktime = 1
    elif t_diff >= 4:
        breaktime = 0.5
    else:
        breaktime = 0
    h_diff = (t_diff-breaktime)/2

    f = open('static/assets/hwp/(주)광주인공지능센터_휴가신청서.htm')
    r = f.read()

    created_at = data.get('created_at')
    reason = data.get('reason')
    startdate = data.get('startdate')
    enddate = data.get('enddate')
    leaveterm = data.get('leaveterm')
    leavecat = data.get('leavecat')
    r = r.replace("data01", str(myuser.realname))
    r = r.replace("data02", "주임")
    r = r.replace("data03", "지식큐레이션팀")
    if leavecat == "연차":
        r = r.replace("data04", "O")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        start_time = datetime.datetime.combine(datetime.date.today(), opening_time)
        end_time = datetime.datetime.combine(datetime.date.today(), closing_time)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    elif leavecat == "오전 반차":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "O")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        end_time = datetime.datetime.combine(datetime.date.today(), closing_time)
        start_time = end_time - datetime.timedelta(hours=h_diff)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    elif leavecat == "오후 반차":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "O")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        start_time = datetime.datetime.combine(datetime.date.today(), opening_time)
        end_time = start_time + datetime.timedelta(hours=h_diff)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    elif leavecat == "경조 휴가":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "O")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        start_time = datetime.datetime.combine(datetime.date.today(), opening_time)
        end_time = datetime.datetime.combine(datetime.date.today(), closing_time)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    elif leavecat == "공가":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "O")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        start_time = datetime.datetime.combine(datetime.date.today(), opening_time)
        end_time = datetime.datetime.combine(datetime.date.today(), closing_time)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    elif leavecat == "조퇴":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "O")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        r = r.replace("data13", str(datetime.datetime.now().strftime("%H:%M")))
        r = r.replace("data15", "24:00")
    elif leavecat == "결근":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "O")
        r = r.replace("data11", "&nbsp;&nbsp;")
        start_time = datetime.datetime.combine(datetime.date.today(), opening_time)
        end_time = datetime.datetime.combine(datetime.date.today(), closing_time)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    elif leavecat == "병가":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "O")
        start_time = datetime.datetime.combine(datetime.date.today(), opening_time)
        end_time = datetime.datetime.combine(datetime.date.today(), closing_time)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    else:
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        start_time = datetime.datetime.combine(datetime.date.today(), opening_time)
        end_time = datetime.datetime.combine(datetime.date.today(), closing_time)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    r = r.replace("data12", str(startdate))
    r = r.replace("data14", str(enddate))
    r = r.replace("data16", str(leaveterm))
    r = r.replace("data17", str(reason))
    r = r.replace("data18", str(created_at)[:str(created_at).find('일')+1])

    return r