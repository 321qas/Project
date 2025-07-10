from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('find_id/', views.find_id, name='find_id'),
    path('find_password/', views.find_password, name='find_password'),
    path('signup/terms/', views.signup_terms, name='signup_terms'),
    path('signup/account/', views.signup_account, name='signup_account'),
    path('signup/verify/', views.signup_verify, name='signup_verify'),
    path('verify-email/', views.verify_email, name='verify_email'),  # 인증링크 콜백용
    path('pw_reset/', views.pw_reset, name='pw_reset'), # get방식 호출 불가
]
