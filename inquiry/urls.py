from django.urls import path, include
from . import views

app_name = 'inquiry'
urlpatterns = [
    path('support/', views.user_support, name='user_support'),
    path('support/my_posts/', views.my_posts, name='my_posts'),
    path('support/all_posts/', views.all_posts, name='all_posts'),
    path('write/', views.inquiry_write, name='inquiry_write'),
]
