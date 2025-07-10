from django.urls import path,include
from . import views

app_name='shortforms'
urlpatterns = [
    path('list/', views.list, name='list'),
    path('upload/', views.upload, name='upload'),
    path('search/', views.search, name='search'),
]
   