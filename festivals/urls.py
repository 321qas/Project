from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'festivals'
urlpatterns = [
    path('festival/<int:pk>/', views.festival_detail, name='festival_detail'),
    path('region_interest_chart/', views.region_interest_chart, name='region_interest_chart'),
]
