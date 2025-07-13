from django.urls import path
from . import views

urlpatterns = [
    path('festival/<int:festival_id>/reviews/', views.review_list, name='review_list'),
    path('festival/<int:festival_id>/reviews/create/', views.review_create, name='review_create'),
    path('review/<int:review_id>/delete/', views.review_delete, name='review_delete'),
    path('review/<int:review_id>/update/', views.review_update, name='review_update'),
    path('review/<int:review_id>/comment/', views.comment_create, name='comment_create'),
    path('comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
]
