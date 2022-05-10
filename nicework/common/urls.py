from django.urls import path
from django.contrib.auth import views as auth_views
from .views import accounts_views, base_views

app_name = 'common'

urlpatterns = [
    # base_views.py
    path('', base_views.index, name='index'),

    # accounts_views.py
    path('signup/', accounts_views.signup, name='signup'),
    path('mypage/', accounts_views.mypage, name='mypage'),
    path('mypage/password/', accounts_views.password, name='password'),

    # auth_views.py
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]