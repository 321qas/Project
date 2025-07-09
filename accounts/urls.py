from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login, name='login'),
    path('lgfor/', views.lgfor, name='lgfor'),
    path('signup/terms/', views.signup_terms, name='signup_terms'),
    path('signup/account/', views.signup_account, name='signup_account'),
    path('signup/verify/', views.signup_verify, name='signup_verify'),
    path('verify-email/', views.verify_email, name='verify_email'),  # 인증링크 콜백용
]
