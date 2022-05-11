from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.models import MyUser
from ..models import LevHistory
from ..forms import LevHistoryForm
import datetime


@login_required(login_url='common:login')
def registration(request):
    # 오전반차의 경우 종료시간, 오후반차의 경우 시작시간 계산
    myuser = get_object_or_404(MyUser, email=request.user.email)
    closing_time = myuser.closingtime
    opening_time = myuser.openingtime
    time_diff = datetime.datetime.combine(datetime.date.today(), closing_time) - datetime.datetime.combine(datetime.date.today(), opening_time)
    t_diff = time_diff.days*24 + time_diff.seconds/3600
    if t_diff >= 8:
        breaktime = 1
    elif t_diff >= 4:
        breaktime = 0.5
    else:
        breaktime = 0
    h_diff = (t_diff - breaktime)/2
    mo_endtime = datetime.datetime.combine(datetime.date.today(), opening_time) + datetime.timedelta(hours=h_diff)
    ao_starttime = datetime.datetime.combine(datetime.date.today(), closing_time) - datetime.timedelta(hours=h_diff)
    mo_endtime = mo_endtime.time()
    ao_starttime = ao_starttime.time()


    if request.method == "POST":
        form = LevHistoryForm(request.POST)
        # 기존 휴가와 겹치는 내용의 신청은 기각
        startdate = request.POST.get('startdate')
        enddate = request.POST.get('enddate')
        start_date = datetime.datetime(int(startdate.split("-")[0]), int(startdate.split("-")[1]), int(startdate.split("-")[2]))
        end_date = datetime.datetime(int(enddate.split("-")[0]), int(enddate.split("-")[1]), int(enddate.split("-")[2]))
        total_leave = LevHistory.objects.filter(employee=myuser)
        not_ovlap1 = LevHistory.objects.filter(employee=myuser, startdate__gte=end_date)
        not_ovlap2 = LevHistory.objects.filter(employee=myuser, enddate__lte=start_date)
        if len(total_leave) != len(not_ovlap1) + len(not_ovlap2):
            messages.error(request, '휴가 신청 내역에 겹치는 기간이 있습니다.')
            return render(request, 'leave/leave_regt.html', {'form': form})
        else: # POST 요청 저장
            if form.is_valid():
                leave_reg = form.save(commit=False)
                leave_reg.employee = myuser
                leaveterm = end_date - start_date + datetime.timedelta(days=1)
                leave_reg.leaveterm = float(leaveterm.days)        
                leave_reg.save()
                return redirect('leave:hist')
    else: # GET 페이지 요청
        form = LevHistoryForm()
        
    context = {'form': form, 'opening_time': str(opening_time), 'closing_time': str(closing_time),
        'mo_endtime': str(mo_endtime), 'ao_starttime': str(ao_starttime), 't_diff': t_diff, 'h_diff': h_diff}
    
    return render(request, 'leave/leave_regt.html', context)