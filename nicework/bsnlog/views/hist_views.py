from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from common.models import MyUser
from ..forms import BusinessLogForm
from ..models import BusinessLog
from django.utils import timezone
from django.core.paginator import Paginator


@login_required(login_url='common:login')
def history(request):
    # 로그인 계정으로 등록한 일지 리스트 가져오기
    myuser = get_object_or_404(MyUser, email=request.user.email)
    mylist = BusinessLog.objects.filter(employee=myuser).order_by('-created_at')

    # 페이지 당 10개씩 보여주기
    page = request.GET.get('page', '1')
    paginator = Paginator(mylist, 10)    
    page_obj = paginator.get_page(page)

    context = {'mylist': page_obj}
    return render(request, 'bsnlog/bsnlog_hist.html', context)


@login_required(login_url='common:login')
def update(request, bsnlog_id):
    businesslog = get_object_or_404(BusinessLog, pk=bsnlog_id)

    # 일지 작성자가 로그인한 계정과 다른지 확인
    if request.user != businesslog.employee:
        messages.error(request, '수정권한이 없습니다')
        return redirect('bsnlog:hist')

    if request.method == "POST": # 양식 작성하여 POST
        form = BusinessLogForm(request.POST)
        if form.is_valid():
            businesslog.contents = form.cleaned_data.get('contents')
            businesslog.updated_at = timezone.now()
            businesslog.save()
            return redirect('bsnlog:hist')
    else: # GET 페이지 요청
        form = BusinessLogForm()

    context = {'form': form, 'contents': businesslog.contents}
    return render(request, 'bsnlog/bsnlog_updt.html', context)