from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from common.models import MyUser
from ..models import CmtHistory
from django.core.paginator import Paginator


@login_required(login_url='common:login')
def history(request):
    # 로그인한 계정의 출퇴근 내역 가져오기
    myuser = get_object_or_404(MyUser, email=request.user.email)
    mylist = CmtHistory.objects.filter(employee=myuser).order_by('-startdatetime')

    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    paginator = Paginator(mylist, 10)
    page_obj = paginator.get_page(page)

    context = {'mylist': page_obj}
    return render(request, 'commute/commute_hist.html', context)