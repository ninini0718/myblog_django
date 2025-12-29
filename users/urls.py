from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    # 用户资料
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change_password/', views.change_password, name='change_password'),
    path('<str:username>/', views.user_profile, name='user_profile'),

    # 用户文章列表
    path('articles/', views.user_articles, name='user_articles'),

    # 用户关注/粉丝
    path('following/', views.following_list, name='following'),
    path('followers/', views.followers_list, name='followers'),

    # 关注/取消关注
    path('follow/<str:username>/', views.follow_user, name='follow'),
    path('unfollow/<str:username>/', views.unfollow_user, name='unfollow'),
    # AJAX 无刷新关注接口
    path('api/follow/<str:username>/', views.follow_ajax, name='follow_ajax'),
    path('api/unfollow/<str:username>/', views.unfollow_ajax, name='unfollow_ajax'),
    # 用户主题设置（AJAX）
    path('api/set_theme/', views.set_theme, name='set_theme'),

    # 🔧 密码找回流程
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset_form.html'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]
