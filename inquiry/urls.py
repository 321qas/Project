from django.urls import path, include
from . import views

app_name = 'inquiry'
urlpatterns = [
    path('support/', views.user_support, name='user_support'),
    path('write/', views.inquiry_write, name='inquiry_write'),
]
