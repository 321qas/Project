from django.urls import path, include
from . import views

app_name = 'inquiry'
urlpatterns = [
    path('support/', views.support, name='support'),
    path('write/', views.write, name='write'),
]
