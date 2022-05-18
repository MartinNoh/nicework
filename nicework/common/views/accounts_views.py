from django.contrib.auth import authenticate, login
from common.models import MyUser
from django.shortcuts import render, redirect, get_object_or_404
from common.admin import UserCreationForm, UserChangeForm
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash


def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=raw_password)  # 사용자 인증
            login(request, user)  # 로그인
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'common/signup.html', {'form': form})


@login_required(login_url='common:login')
def mypage(request):
    try:
        whois = get_object_or_404(MyUser, email=request.user.email)
    except Exception as e:
        whois = ''
        print(f"Exceiption occured:\n{e}")

    if request.method == "POST":
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            myuser = form.save(commit=False)
            myuser.updated_at = timezone.now()
            myuser.save()
            return redirect('index')
        else:
            is_fine = False
    else:
        is_fine = True
        form = UserChangeForm(instance=request.user)
    return render(request, 'common/mypage.html', {'myuser':whois, 'form': form, 'is_fine': is_fine, 'email': request.user.email})



@login_required(login_url='common:login')
def password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)
        if form.is_valid():
            user = form.save()
            # 비밀번호를 바꾸면 기존 세션과 일치하지 않게 되어 로그아웃된다. 이를 방지하기 위한 auth_hash 갱신.
            update_session_auth_hash(request, user)
            return redirect('common:mypage')
    else:
        form = PasswordChangeForm(request.user)
    context = {'form':form}
    return render(request, 'common/password.html', context)