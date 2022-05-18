from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from common.models import MyUser
from ..models import CmtHistory
from leave.models import LevHistory
from django.utils import timezone
import datetime
import math
from pytimekr import pytimekr


@login_required(login_url='common:login')
def registration(request, check_result):
    # 로그인한 계정
    myuser = get_object_or_404(MyUser, email=request.user.email)
    if myuser.is_mgr or myuser.is_admin:
        return redirect('commute:situ')
        
    # 오늘 관련
    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.time(0, 0, 0))
    today_end = datetime.datetime.combine(today, datetime.time(23, 59, 59))
    today_weekday = today.weekday()
    weekday_dict = {"0":"월요일", "1":"화요일", "2":"수요일", "3":"목요일", "4":"금요일", "5":"토요일", "6":"일요일"}
    today_week = datetime.datetime.now().isocalendar()[1]

    # 계정의 평소 출퇴근 시간, 휴게 시간
    openingtime = myuser.openingtime
    closingtime = myuser.closingtime
    time_diff = datetime.datetime.combine(today, closingtime) - datetime.datetime.combine(today, openingtime)
    t_diff = time_diff.days*24 + time_diff.seconds/3600
    if t_diff >= 8:
        breaktime = 1
    elif t_diff >= 4:
        breaktime = 0.5
    else:
        breaktime = 0
    h_diff = (t_diff-breaktime)/2    

    # 휴일여부, 시업시간, 종업 시간
    holiday_list = pytimekr.holidays(datetime.datetime.now().year)
    todaycat_dict = {"AL":"연차", "MO":"오전 반차", "AO":"오후 반차", "CV":"경조 휴가", "OL":"공가", "EL":"조퇴", "AB":"결근", "SL":"병가", "HD":"공휴일", "WE":"주말", "WD":"평일"}
    leave_today_list = LevHistory.objects.filter(employee=myuser, startdate__lte=today, enddate__gte=today, approval='3').order_by('-startdate')
    modified_closingtime = None
    modified_openingtime = None
    if today in holiday_list:
        todaycat = "HD"
    elif today_weekday > 4:
        todaycat = "WE"
    elif leave_today_list:
        leavecat = leave_today_list[0].leavecat
        if str(leavecat) == 'MO':
            todaycat = str(leavecat)
            modified_openingtime = datetime.datetime.combine(today, openingtime) + datetime.timedelta(hours=h_diff)
            modified_openingtime = modified_openingtime.time()
            modified_closingtime = closingtime
        elif str(leavecat) == 'AO':
            todaycat = str(leavecat)
            modified_openingtime = openingtime
            modified_closingtime = datetime.datetime.combine(today, closingtime) - datetime.timedelta(hours=h_diff)
            modified_closingtime = modified_closingtime.time()
        else:
            todaycat = str(leavecat)
    else:
        todaycat = "WD"
        modified_openingtime = openingtime
        modified_closingtime = closingtime


    """
    출퇴근 PAGE CASE
    1-1. 이전 출근 기록 없음, 오늘 출근 기록 없음 -> [계정 첫 출근] 표시 페이지는 출근
    1-2. 이전 출근 기록 없음, 오늘 출근 기록 있음 -> [계정 첫 퇴근] 표시 페이지는 퇴근
    1-3. 이전 출근 기록 있음, 이전 퇴근 기록 없음 -> [퇴근 버튼 안누르고 감, 철야] 표시 페이지는 출근, 바로 전 날짜 퇴근은 종업시간으로 변경 처리, 비정상 True
    1-4. 이전 출근 기록 있음, 이전 퇴근 기록 있음, 오늘 출근 기록 없음 -> [오늘 정상 출근] 표시 페이지는 출근
    1-5. 이전 출근 기록 있음, 이전 퇴근 기록 있음, 오늘 출근 기록 있음 -> [오늘 정상 출근했고, 퇴근, 야근] 표시 페이지는 퇴근
    """
    # 오늘 출근 기록, 최근 출근 기록 리스트
    today_commute_list = CmtHistory.objects.filter(employee=myuser, startdatetime__gte=today_start, startdatetime__lte=today_end).order_by('startdatetime')
    recent_commute_list = CmtHistory.objects.filter(employee=myuser, startdatetime__lte=today_start).order_by('-startdatetime')
    
    """
    근무시간 계산 CASE
    2-1. 시업시간보다 늦은 출근으로 지각 : 근무 시간 = 퇴근 시간 - 출근 시간
    2-2. 1시간 이내, 시업시간보다 이른 출근 : 근무 시간 = 퇴근 시간 - 시업 시간
    2-3. 1시간 초과, 시업시간보다 이른 출근 : 근무 시간 = 퇴근 시간 - 출근 시간
    """

    is_getoff = False

    # 출퇴근 페이지 구분
    if recent_commute_list and len(recent_commute_list) > 0 and recent_commute_list[0].enddatetime is None: # CASE 1-3
        is_getoff = False
        
        # 근무시간, 휴게시간, 연장근로시간
        lastwork_openingtime = recent_commute_list[0].openingtime
        lastwork_starttime = recent_commute_list[0].startdatetime.time()
        start_diff = datetime.datetime.combine(today, lastwork_openingtime) - datetime.datetime.combine(today, lastwork_starttime)
        st_diff = start_diff.days*24 + start_diff.seconds/3600
        if st_diff >= 0 and st_diff <= 1: # CASE 2-2
            workinghours = datetime.datetime.combine(today, closingtime) - datetime.datetime.combine(today, lastwork_openingtime)  
        else: # CASE 2-1, 2-3
            workinghours = datetime.datetime.combine(today, closingtime) - datetime.datetime.combine(today, lastwork_starttime)
        wk_hours = workinghours.days*24 + workinghours.seconds/3600
        breaktime = wk_hours // 4 * 0.5
        overtime = wk_hours - t_diff if wk_hours - t_diff > 0 else 0

        recent_commute_list[0].enddatetime = datetime.datetime.combine(recent_commute_list[0].startdatetime.date(), myuser.closingtime)
        recent_commute_list[0].is_abnormal = True
        recent_commute_list[0].breaktime = round(breaktime, 1)
        recent_commute_list[0].overtime = round(overtime, 1)
        recent_commute_list[0].workinghours = round((wk_hours-breaktime), 1)
        recent_commute_list[0].save()
    else:
        is_getoff = True if today_commute_list and len(today_commute_list) > 0 else False # if: CASE 1-2, 1-5, else: CASE 1-1, 1-4
   

    # 출근 버튼 클릭
    if check_result == "start":
        CmtHistory.objects.create(employee=myuser, weeknum=today_week, todaycat=todaycat, openingtime=modified_openingtime, closingtime=modified_closingtime, startdatetime=timezone.now())
        return redirect('/commute/regt/check/')


    # 퇴근 버튼 클릭
    elif check_result == "end":
        lastwork = CmtHistory.objects.filter(employee=myuser, startdatetime__gte=today_start, startdatetime__lte=today_end).order_by('startdatetime')[0]
        """
        # 출근한 지 5분 미만인 인스턴스는 퇴근 버튼 누르면 삭제
        if datetime.datetime.now() < lastwork.startdatetime + datetime.timedelta(minutes=5):
            lastwork.delete()
            return redirect('/commute/regt/check/')
        else:
        """
        # 근무시간, 휴게시간, 연장근로시간 계산
        lastwork_openingtime = lastwork.openingtime
        lastwork_starttime = lastwork.startdatetime.time()
        start_diff = datetime.datetime.combine(today, lastwork_openingtime) - datetime.datetime.combine(today, lastwork_starttime)
        st_diff = start_diff.days*24 + start_diff.seconds/3600
        if st_diff >= 0 and st_diff <= 1: # Good Case
            workinghours = datetime.datetime.combine(today, timezone.now().time()) - datetime.datetime.combine(today, lastwork_openingtime)  
        else: # Bad Case, Excellent Case
            workinghours = datetime.datetime.combine(today, timezone.now().time()) - datetime.datetime.combine(today, lastwork_starttime)
        wk_hours = workinghours.days*24 + workinghours.seconds/3600
        breaktime = wk_hours // 4 * 0.5
        overtime = wk_hours - t_diff if wk_hours - t_diff > 0 else 0

        # 퇴근 시간 업데이트
        lastwork.enddatetime = timezone.now()
        lastwork.breaktime = round(breaktime, 1)
        lastwork.overtime = round(overtime, 1)
        lastwork.workinghours = round((wk_hours-breaktime), 1)
        lastwork.save()

        return redirect('commute:hist')

    # 이번 주 잔여 근로시간, 잔여 연장근로시간
    total_worktime = 0
    total_overtime = 0
    week_list = CmtHistory.objects.filter(employee=myuser, weeknum=today_week).order_by('-startdatetime')
    if week_list:
        for i in week_list:
            total_worktime += i.workinghours
            total_overtime += i.overtime
    remain_worktime = int(40 - total_worktime)
    remain_overtime = int(12 - total_overtime)

    context = {'is_getoff': is_getoff, 'today': today, 'today_week': today_week, 'today_weekday': weekday_dict[str(today_weekday)], 'remain_worktime': remain_worktime, 'remain_overtime': remain_overtime,
                'closingtime': closingtime, 'openingtime': openingtime, 'todaycat': todaycat_dict[str(todaycat)], 'modified_closingtime': modified_closingtime, 'modified_openingtime':modified_openingtime}

    return render(request, 'commute/commute_regt.html', context)