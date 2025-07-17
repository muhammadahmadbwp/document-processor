from django.urls import path
from . import views

urlpatterns = [
    path('', views.diagnostics_dashboard, name='diagnostics_dashboard'),
    path('connectivity/', views.api_connectivity_check, name='connectivity_check'),
    path('logging/', views.logging_check, name='logging_check'),
    path('celery/', views.celery_check, name='celery_check'),
    path('cache/', views.cache_check, name='cache_check'),
    path('middleware/', views.middleware_check, name='middleware_check'),
    path('system-info/', views.system_info, name='system_info'),
    path('celery/test-success/', views.celery_test_success, name='celery_test_success'),
    path('celery/test-retry/', views.celery_test_retry, name='celery_test_retry'),
    path('celery/test-failure/', views.celery_test_failure, name='celery_test_failure'),
    path('celery/test-long/', views.celery_test_long, name='celery_test_long'),
    path('celery/revoke-task/', views.celery_revoke_task, name='celery_revoke_task'),
    path('celery/task-status/', views.celery_task_status, name='celery_task_status'),
    
    # New Logging test endpoints
    path('logging/config/', views.logging_config, name='logging_config'),
    path('logging/test-all-levels/', views.logging_test_all_levels, name='logging_test_all_levels'),
    path('logging/test-celery/', views.logging_test_celery, name='logging_test_celery'),
    path('logging/view-log-file/', views.view_log_file, name='view_log_file'),
]
