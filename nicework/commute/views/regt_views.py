from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from common.models import MyUser
from ..models import Commute
from leave.models import Leave
from django.utils import timezone
import datetime
import math
from pytimekr import pytimekr


@login_required(login_url='common:login')
def registration(request, check_result):
    """
    출퇴근 페이지 구분 CASE
    1. 이전 출근 기록 없음, 오늘 출근 기록 없음 [계정 첫 출근] -> 표시 페이지는 출근
    2. 이전 출근 기록 없음, 오늘 출근 기록 있음 [계정 첫 퇴근] -> 표시 페이지는 퇴근
    3. 이전 출근 기록 있음, 이전 퇴근 기록 없음 [퇴근 버튼 안누르고 감, 철야] -> 표시 페이지는 출근, 바로 전 날짜 퇴근은 종업시간으로 변경 처리, 비정상 True
    4. 이전 출근 기록 있음, 이전 퇴근 기록 있음, 오늘 출근 기록 없음 [오늘 정상 출근] -> 표시 페이지는 출근
    5. 이전 출근 기록 있음, 이전 퇴근 기록 있음, 오늘 출근 기록 있음 [오늘 정상 출근했고, 퇴근, 야근] -> 표시 페이지는 퇴근
    """
    is_getoff = False
    # 오늘, 최근 출근 기록 가져오기
    today = datetime.date.today()
    today_start = datetime.datetime.combine(today, datetime.time(0, 0, 0))
    today_end = datetime.datetime.combine(today, datetime.time(23, 59, 59))
    myuser = get_object_or_404(MyUser, email=request.user.email)
    recent_list = Commute.objects.filter(employee=myuser, startdatetime__lte=today_start).order_by('-startdatetime')
    today_list = Commute.objects.filter(employee=myuser, startdatetime__gte=today_start, startdatetime__lte=today_end).order_by('startdatetime')

    # 출퇴근 페이지 구분
    if recent_list and len(recent_list) > 0 and recent_list[0].enddatetime is None: # CASE 3
        is_getoff = False
        recent_list[0].enddatetime = myuser.closingtime
        recent_list[0].is_abnormal = True
        recent_list[0].save()
    else:
        is_getoff = True if today_list and len(today_list) > 0 else False # if: CASE 2, 5, else: CASE 1, 4


    """
    출퇴근 상세 정보
    """
    # 금주 남은 근로시간, 연장근로시간
    today_week = datetime.datetime.now().isocalendar()[1]
    week_list = Commute.objects.filter(employee=myuser, weeknum=today_week).order_by('-startdatetime')
    total_worktime = 0
    total_overtime = 0
    if week_list:
        for i in week_list:
            total_worktime += i.workinghours
            total_overtime += i.overtime
    remain_worktime = 40 - total_worktime
    remain_overtime = 12 - total_overtime

    # 계정 평소 출근 시간, 퇴근 시간
    closingtime = myuser.closingtime
    openingtime = myuser.openingtime
    time_diff = datetime.datetime.combine(today, closingtime) - datetime.datetime.combine(today, openingtime)
    t_diff = time_diff.days*24 + time_diff.seconds/3600

    # 휴가, 공휴일, 주말, 평일 구분을 적용한 시업, 종업 시간
    holiday_list = pytimekr.holidays(datetime.datetime.now().year)
    today_weekday = today.weekday()
    leave_with_today_list = Leave.objects.filter(startdate__lte=today, enddate__gte=today, is_approved=True).order_by('-startdate')
    weekday_dict = {"0":"월요일", "1":"화요일", "2":"수요일", "3":"목요일", "4":"금요일", "5":"토요일", "6":"일요일"}
    todaycat_dict = {"AL":"연차", "MO":"오전 반차", "AO":"오후 반차", "CV":"경조 휴가", "OL":"공가", "EL":"조퇴", "AB":"결근", "SL":"병가"
        , "HD":"공휴일", "WE":"주말", "WD":"평일"}
    modified_closingtime = None
    modified_openingtime = None
    if today in holiday_list:
        todaycat = "HD"
    elif today_weekday > 4:
        todaycat = "WE"
    elif leave_with_today_list:
        leavecat = leave_with_today_list[0].leavecat
        if str(leavecat) == 'MO':
            todaycat = str(leavecat)
            modified_openingtime = openingtime + datetime.timedelta(hours=t_diff)
            modified_closingtime = closingtime
        elif str(leavecat) == 'AO':
            todaycat = str(leavecat)
            modified_openingtime = openingtime
            modified_closingtime = closingtime - datetime.timedelta(hours=t_diff)
        else:
            todaycat = str(leavecat)
    else:
        todaycat = "WD"
        modified_openingtime = openingtime
        modified_closingtime = closingtime

    context = {'is_getoff': is_getoff, 'today': today, 'today_week': today_week, 'today_weekday': weekday_dict[str(today_weekday)], 
                'remain_worktime': remain_worktime, 'remain_overtime': remain_overtime,
                'closingtime': closingtime, 'openingtime': openingtime, 'todaycat': todaycat_dict[str(todaycat)], 'modified_closingtime': modified_closingtime, 'modified_openingtime':modified_openingtime}
    

    # 출근 버튼 클릭
    if check_result == "start":
        Commute.objects.create(employee=myuser, weeknum=today_week, todaycat=todaycat, openingtime=modified_openingtime, closingtime=modified_closingtime, startdatetime=timezone.now())
        return redirect('/commute/regt/check/')

    # 퇴근 버튼 클릭
    elif check_result == "end":
        lastwork = Commute.objects.filter(employee=myuser, startdatetime__gte=today_start, startdatetime__lte=today_end).order_by('startdatetime')[0]
        # 출근한 지 1시간 미만인 인스턴스는 퇴근 버튼 누르면 삭제
        if datetime.datetime.now() < lastwork.startdatetime + datetime.timedelta(hours=1):
            lastwork.delete()
            return redirect('/commute/regt/check/')
        else:
            """
            근무 시간 계산 CASE
            Bad Case, 시업 시간보다 늦은 출근 : 근무 시간 = 퇴근 시간 - 출근 시간
            Good Case, 1시간 이내, 시업 시간보다 이른 출근 : 근무 시간 = 퇴근 시간 - 시업 시간
            Excellent Case, 1시간 초과, 시업 시간보다 이른 출근 : 근무 시간 = 퇴근 시간 - 출근 시간
            9시간 근무 = 8시간 실제 근무 + 휴게 1시간
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
            workinghours = wk_hours - breaktime

            # 퇴근 시간 업데이트
            lastwork.enddatetime = timezone.now()
            lastwork.breaktime = breaktime
            lastwork.overtime = overtime
            lastwork.workinghours = workinghours
            lastwork.save()

            return redirect('/')

    return render(request, 'commute/commute_regt.html', context)