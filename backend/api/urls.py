from django.contrib import admin
from django.urls import path

from api import views

urlpatterns = [
    path('api/v1/comments/', views.get_all_comments, name='get_all_comments'),
    path('api/v1/comments/upsert/', views.upsert_comment, name='upsert_comment'),
    path('api/v1/comments/<str:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
