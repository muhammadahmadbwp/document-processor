import logging
import time
from celery import shared_task
from django.core.cache import cache
from celery.result import AsyncResult
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(bind=True)
def test_success_task(self, sleep_time=2):
    """A task that succeeds after sleeping for the specified time."""
    task_id = self.request.id
    logger.info(f"Starting success task {task_id}")
    time.sleep(sleep_time)
    logger.info(f"Completing success task {task_id}")
    return {"task_id": task_id, "status": "completed", "result": "success"}

@shared_task(bind=True, max_retries=3)
def test_retry_task(self, sleep_time=2):
    """A task that retries itself a few times before succeeding."""
    task_id = self.request.id
    retry_count = self.request.retries
    logger.info(f"Starting retry task {task_id} (attempt {retry_count+1})")
    time.sleep(sleep_time)
    
    if retry_count < 2:  # Retry twice, succeed on third attempt
        logger.info(f"Retrying task {task_id}")
        raise self.retry(countdown=1)
    
    logger.info(f"Completing retry task {task_id} after {retry_count+1} attempts")
    return {"task_id": task_id, "status": "completed", "retries": retry_count}

@shared_task(bind=True)
def test_failure_task(self, sleep_time=2):
    """A task that deliberately fails."""
    task_id = self.request.id
    logger.info(f"Starting failure task {task_id}")
    time.sleep(sleep_time)
    logger.error(f"Task {task_id} is about to fail")
    raise ValueError("This task is designed to fail")

@shared_task(bind=True)
def test_long_task(self, sleep_time=30):
    """A long-running task that can be revoked."""
    task_id = self.request.id
    logger.info(f"Starting long task {task_id}")
    
    # Sleep in small increments to allow for revocation
    for i in range(sleep_time):
        time.sleep(1)
        if i % 5 == 0:
            logger.info(f"Long task {task_id} still running ({i}/{sleep_time}s)")
    
    logger.info(f"Completing long task {task_id}")
    return {"task_id": task_id, "status": "completed", "duration": sleep_time}

def get_task_status(task_id):
    """Get the status of a task by its ID."""
    # First check our cache for custom status
    cached_status = cache.get(f"task_status_{task_id}")
    if cached_status:
        return cached_status
    
    # Otherwise use Celery's built-in status
    result = AsyncResult(task_id)
    return result.state
