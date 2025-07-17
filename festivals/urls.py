from django.contrib import admin
from django.urls import path, include
from . import views

app_name = 'festivals'
urlpatterns = [
    path('Statistics_chart/', views.Statistics_chart, name='Statistics_chart'),
    path('view/<int:id>/', views.view, name='view'),
    path('list/', views.list, name='list'),
    path('search/',views.search,name='search'),
]
