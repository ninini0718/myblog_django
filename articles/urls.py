# articles/urls.py

from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('create/', views.create_article, name='create_article'),
    path('edit/<slug:slug>/', views.edit_article, name='edit_article'),
    path('<slug:slug>/', views.article_detail, name='article_detail'),
    path('', views.article_list, name='article_list'),
    path('delete/<slug:slug>/', views.delete_article, name='delete_article'),  # 修改这里
    path('like/<slug:slug>/', views.like_article, name='like_article'),
    path("qrcode/<slug:slug>/", views.article_qrcode, name="article_qrcode"),
]
