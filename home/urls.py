from django.urls import path,include
from . import views

app_name=''
urlpatterns = [
    path('', views.index, name='index'),
    path('jlist/', views.jlist, name='jlist'),
    path('slist/', views.slist, name='slist_all'), # sno가 없는 경우
    path('slist/<int:sno>/', views.slist, name='slist_with_id'),
    path('<int:sno>/', views.first, name='first'),
]
