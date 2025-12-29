from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/<int:user_id>/action/', views.admin_user_action, name='admin_user_action'),
    path('admin/articles/', views.admin_articles, name='admin_articles'),
    path('admin/articles/<int:article_id>/edit/', views.admin_edit_article, name='admin_edit_article'),
    path('admin/articles/<int:article_id>/delete/', views.admin_delete_article, name='admin_delete_article'),
    path('admin/comments/', views.admin_comments, name='admin_comments'),
    path('admin/comments/<int:comment_id>/delete/', views.admin_delete_comment, name='admin_delete_comment'),
    path('admin/settings/', views.admin_settings, name='admin_settings'),
    path('test-email/', views.test_email_providers, name='test_email'),
    path('send-test-email/', views.send_test_email, name='send_test_email'),
]
