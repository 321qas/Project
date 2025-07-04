from django.urls import path, include
from . import views

app_name = 'shortforms'
urlpatterns = [
    path('upload/', views.upload, name='upload'),
]
