from __future__ import absolute_import, unicode_literals
import os
import logging
from celery import Celery
from celery.signals import after_setup_logger, after_setup_task_logger, task_success, task_failure, task_revoked, task_retry
from celery.utils.log import get_task_logger
from django.core.cache import cache
from document_processor.settings.base import CELERY_LOG_DIR

CELERY_LOG_DIR.mkdir(exist_ok=True)
CELERY_LOG_FILE = CELERY_LOG_DIR / 'celery.log'

logger = get_task_logger(__name__)

# Set the appropriate settings module based on environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', os.getenv('DJANGO_SETTINGS_MODULE'))

app = Celery('document_processor')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Configure Celery logging
@after_setup_logger.connect
@after_setup_task_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s %(module)s %(filename)s %(funcName)s %(lineno)d %(request_id)s %(process)d %(thread)d %(message)s'
    )
    
    # File handler for Celery logs
    file_handler = logging.FileHandler(str(CELERY_LOG_FILE))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.ERROR)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')

@task_success.connect
def handle_task_success(task_id, result, **kw):
    logger.info(f"Task {task_id} succeeded with result: {result}")

# Error handling for Celery tasks
@task_failure.connect
def handle_task_failure(task_id, exception, args, kwargs, traceback, einfo, **kw):
    logger.error(
        f"Task {task_id} failed: {str(exception)}\n"
        f"Args: {args}\n"
        f"Kwargs: {kwargs}\n"
        f"Traceback: {traceback}"
    )

@task_retry.connect
def handle_task_retry(request, args, kwargs, eta, **kw):
    logger.warning(f"Task {request.id} is being retried with ETA: {eta}")

@task_revoked.connect
def handle_task_revoked(request, **kw):
    logger.warning(f"Task {request.id} was revoked")