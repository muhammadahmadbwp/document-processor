from django.shortcuts import render
import logging
import time
from django.http import JsonResponse, HttpResponse
from django.core.cache import cache
from django.views.decorators.http import require_http_methods
from celery import shared_task
from django.conf import settings
from .celery_tests import (
    test_success_task, test_retry_task, test_failure_task, 
    test_long_task, get_task_status
)
from .logging_tests import (
    get_logger_info, get_log_files, test_all_log_levels,
    test_celery_logging, get_recent_log_entries
)
from pathlib import Path
from celery.app.control import Control
from document_processor.celery import app as celery_app

control = Control(app=celery_app)

logger = logging.getLogger(__name__)

def diagnostics_dashboard(request):
    """Render the diagnostics dashboard."""
    return render(request, 'diagnostics.html')

@require_http_methods(["GET"])
def api_connectivity_check(request):
    """Simple API to check if the server is responding."""
    logger.info("Connectivity check performed")
    return JsonResponse({
        "status": "ok",
        "message": "API server is running"
    })

@require_http_methods(["GET"])
def logging_check(request):
    """Test that logging is working properly."""
    logger.debug("This is a DEBUG message")
    logger.info("This is an INFO message")
    logger.warning("This is a WARNING message")
    logger.error("This is an ERROR message")
    
    return JsonResponse({
        "status": "ok",
        "message": "Logging check completed. Check your log files."
    })

@shared_task
def sample_celery_task(task_id):
    """A sample Celery task that sleeps for 5 seconds and returns a result."""
    logger.info(f"Starting Celery task {task_id}")
    time.sleep(5)
    logger.info(f"Completed Celery task {task_id}")
    return {"task_id": task_id, "status": "completed"}

@require_http_methods(["GET"])
def celery_check(request):
    """Test that Celery is working properly."""
    task_id = str(time.time())
    task = sample_celery_task.delay(task_id)
    
    return JsonResponse({
        "status": "ok",
        "message": "Celery task submitted",
        "task_id": task_id,
        "celery_task_id": task.id
    })

@require_http_methods(["GET"])
def cache_check(request):
    """Test that cache is working properly."""
    cache_key = "diagnostic_test"
    cache_value = str(time.time())
    
    # Set a value in the cache
    cache.set(cache_key, cache_value, 60)
    
    # Retrieve the value from the cache
    retrieved_value = cache.get(cache_key)
    
    return JsonResponse({
        "status": "ok" if retrieved_value == cache_value else "error",
        "message": "Cache is working" if retrieved_value == cache_value else "Cache is not working",
        "set_value": cache_value,
        "retrieved_value": retrieved_value
    })

@require_http_methods(["GET"])
def middleware_check(request):
    """Test that middleware is processing requests."""
    # This will show all headers, including those added by middleware
    headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
    
    return JsonResponse({
        "status": "ok",
        "message": "Middleware check",
        "headers": headers,
        "middleware_classes": str(settings.MIDDLEWARE)
    })

@require_http_methods(["GET"])
def system_info(request):
    """Return basic system information."""
    import platform
    import django
    import sys
    
    return JsonResponse({
        "status": "ok",
        "python_version": platform.python_version(),
        "django_version": django.__version__,
        "platform": platform.platform(),
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "debug_mode": settings.DEBUG
    })

@require_http_methods(["GET"])
def celery_test_success(request):
    """Test a Celery task that succeeds."""
    task = test_success_task.delay(2)
    return JsonResponse({
        "status": "submitted",
        "task_id": task.id,
        "task_type": "success",
        "message": "Task submitted successfully"
    })

@require_http_methods(["GET"])
def celery_test_retry(request):
    """Test a Celery task that retries."""
    task = test_retry_task.delay(1)
    return JsonResponse({
        "status": "submitted",
        "task_id": task.id,
        "task_type": "retry",
        "message": "Task submitted successfully"
    })

@require_http_methods(["GET"])
def celery_test_failure(request):
    """Test a Celery task that fails."""
    task = test_failure_task.delay(1)
    return JsonResponse({
        "status": "submitted",
        "task_id": task.id,
        "task_type": "failure",
        "message": "Task submitted successfully"
    })

@require_http_methods(["GET"])
def celery_test_long(request):
    """Test a long-running Celery task."""
    task = test_long_task.delay(30)
    return JsonResponse({
        "status": "submitted",
        "task_id": task.id,
        "task_type": "long",
        "message": "Long task submitted successfully"
    })

@require_http_methods(["GET"])
def celery_revoke_task(request):
    """Revoke a running Celery task."""
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({
            "status": "error",
            "message": "No task_id provided"
        }, status=400)
    
    control.revoke(task_id, terminate=True)
    
    return JsonResponse({
        "status": "revoked",
        "task_id": task_id,
        "message": "Task revocation request sent"
    })

@require_http_methods(["GET"])
def celery_task_status(request):
    """Get the status of a Celery task."""
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({
            "status": "error",
            "message": "No task_id provided"
        }, status=400)
    
    status = get_task_status(task_id)
    
    return JsonResponse({
        "task_id": task_id,
        "status": status
    })

@require_http_methods(["GET"])
def logging_config(request):
    """Get information about the current logging configuration."""
    return JsonResponse({
        "logger_info": get_logger_info(),
        "log_files": get_log_files()
    })

@require_http_methods(["GET"])
def logging_test_all_levels(request):
    """Test logging at all levels."""
    results = test_all_log_levels()
    return JsonResponse({
        "status": "completed",
        "results": results
    })

@require_http_methods(["GET"])
def logging_test_celery(request):
    """Test Celery task logging."""
    results = test_celery_logging()
    return JsonResponse({
        "status": "submitted",
        "results": results
    })

@require_http_methods(["GET"])
def view_log_file(request):
    """View the contents of a log file."""
    log_path = request.GET.get('path')
    if not log_path:
        return JsonResponse({
            "status": "error",
            "message": "No log file path provided"
        }, status=400)
    
    log_path = Path(log_path)
    
    # Basic security check to ensure we're only reading log files
    if not str(log_path).endswith('.log'):
        return JsonResponse({
            "status": "error",
            "message": "Invalid log file path"
        }, status=400)
    
    if not log_path.exists():
        return JsonResponse({
            "status": "error",
            "message": "Log file does not exist"
        }, status=404)
    
    content = get_recent_log_entries(log_path)
    
    return HttpResponse(content, content_type='text/plain')