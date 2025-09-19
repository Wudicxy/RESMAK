# resumes/urls.py
from django.urls import path
from . import views, api, views_debug
from .views_debug import debug_text_dashboard  # 新增

app_name = 'resumes'

urlpatterns = [
    # 首页/仪表盘
    path('', views.dashboard, name='dashboard'),

    # 新建改写文本调试
    path('debug-text/', views_debug.debug_text_dashboard, name='debug_text_dashboard'),
    path('result/<int:pk>/', views.result, name='result'),
    path('api/rewrite/', api.RewriteView.as_view(), name='api_rewrite'),
    path('debug-text/', debug_text_dashboard, name='debug_text'),  # 新增调试入口
    path('history/', views.resume_history, name='history'),
    path('history/<int:resume_id>/', views.resume_detail, name='resume_detail'),
    path('result/<int:result_id>/', views.rewrite_result_detail, name='result_detail'),
]
