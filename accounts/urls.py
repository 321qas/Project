from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('lgfor/', views.lgfor, name='lgfor'),
    path('signup/terms/', views.signup_terms, name='signup_terms'),
    path('signup/account/', views.signup_account, name='signup_account'),
    path('id_check/', views.id_check, name='id_check'), # 아이디 중복확인 자바스크립트용
    path('nick_check/', views.nick_check, name='nick_check'), # 닉네임 중복확인 자바스크립트용
    path('mail_check/', views.mail_check, name='mail_check'), # 이메일 중복확인 자바스크립트용
    path('signup/verify/', views.signup_verify, name='signup_verify'),
    path('verify-email/', views.verify_email, name='verify_email'),  # 인증링크 콜백용
]
