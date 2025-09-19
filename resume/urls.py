# resumes/urls.py
from django.urls import path
from . import views, api

app_name = 'resumes'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('result/<int:pk>/', views.result, name='result'),
    path('api/rewrite/', api.RewriteView.as_view(), name='api_rewrite'),
]
