from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('add/', views.add_wishlist, name='add_wishlist'),
    path('count/', views.wishlist_count, name='wishlist_count'),
]
