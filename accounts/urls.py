from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('find_id/', views.find_id, name='find_id'),
    path('find_password/', views.find_password, name='find_password'),
    path('signup/terms/', views.signup_terms, name='signup_terms'),
    path('signup/account/', views.signup_account, name='signup_account'),
    path('id_check/', views.id_check, name='id_check'), # 아이디 중복확인 자바스크립트용
    path('nick_check/', views.nick_check, name='nick_check'), # 닉네임 중복확인 자바스크립트용
    path('mail_check/', views.mail_check, name='mail_check'), # 이메일 중복확인 자바스크립트용
    path('signup/verify/', views.signup_verify, name='signup_verify'),
    path('verify-email/', views.verify_email, name='verify_email'),  # 인증링크 콜백용
    path('mypage1/', views.mypage1, name='mypage1'),  
    path('mypage2/', views.mypage2, name='mypage2'),  
    # path('pw_reset/', views.pw_reset, name='pw_reset'), # get방식 호출 불가
]
