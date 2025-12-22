from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('test-email/', views.test_email_providers, name='test_email'),
    path('send-test-email/', views.send_test_email, name='send_test_email'),
]
