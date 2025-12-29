from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('add/<int:article_id>/', views.add_comment, name='add_comment'),
    path('delete/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('like/<int:comment_id>/', views.like_comment, name='like_comment'),
    path('api/fetch/<int:comment_id>/', views.fetch_comment, name='fetch_comment'),
    path('notifications/json/', views.notifications_json, name='notifications_json'),
    path('notifications/mark/', views.mark_notification, name='mark_notification'),
    path('notifications/', views.notifications_page, name='notifications_page'),
]
