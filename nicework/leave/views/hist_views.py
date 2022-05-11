from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.models import MyUser
from ..models import LevHistory
from django.core.paginator import Paginator
import datetime


@login_required(login_url='common:login')
def history(request):
    # 로그인 계정으로 등록한 휴가 리스트 가져오기
    myuser = get_object_or_404(MyUser, email=request.user.email)
    mylist = LevHistory.objects.filter(employee=myuser).order_by('-created_at')
    
    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    # 한글 파일 다운로드 버튼 클릭
    if request.method == "POST":
        is_download = True
        r = get_leave_hwp(request.POST, myuser)
    else:
        is_download = False
        r = ''

    context = {'mylist': page_obj, 'source_html': r, 'is_download': is_download}
    return render(request, 'leave/leave_hist.html', context)



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
        r = r.replace("data04", "o")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        r = r.replace("data13", "00:00")
        r = r.replace("data15", "24:00")
    elif leavecat == "오전 반차":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "o")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        end_time = datetime.datetime.combine(datetime.date.today(), opening_time) + datetime.timedelta(hours=h_diff)
        r = r.replace("data13", "00:00")
        r = r.replace("data15", str(end_time.strftime("%H:%M")))
    elif leavecat == "오후 반차":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "o")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        start_time = datetime.datetime.combine(datetime.date.today(), closing_time) - datetime.timedelta(hours=h_diff)
        r = r.replace("data13", str(start_time.strftime("%H:%M")))
        r = r.replace("data15", "24:00")
    elif leavecat == "경조 휴가":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "o")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        r = r.replace("data13", "00:00")
        r = r.replace("data15", "24:00")
    elif leavecat == "공가":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "o")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        r = r.replace("data13", "00:00")
        r = r.replace("data15", "24:00")
    elif leavecat == "조퇴":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "o")
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
        r = r.replace("data10", "o")
        r = r.replace("data11", "&nbsp;&nbsp;")
        r = r.replace("data13", "00:00")
        r = r.replace("data15", "24:00")
    elif leavecat == "병가":
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "o")
        r = r.replace("data13", "00:00")
        r = r.replace("data15", "24:00")
    else:
        r = r.replace("data04", "&nbsp;&nbsp;")
        r = r.replace("data05", "&nbsp;&nbsp;")
        r = r.replace("data06", "&nbsp;&nbsp;")
        r = r.replace("data07", "&nbsp;&nbsp;")
        r = r.replace("data08", "&nbsp;&nbsp;")
        r = r.replace("data09", "&nbsp;&nbsp;")
        r = r.replace("data10", "&nbsp;&nbsp;")
        r = r.replace("data11", "&nbsp;&nbsp;")
        r = r.replace("data13", "00:00")
        r = r.replace("data15", "24:00")
    r = r.replace("data12", str(startdate))
    r = r.replace("data14", str(enddate))
    r = r.replace("data16", str(leaveterm))
    r = r.replace("data17", str(reason))
    r = r.replace("data18", str(created_at)[:str(created_at).find('일')+1])

    return r