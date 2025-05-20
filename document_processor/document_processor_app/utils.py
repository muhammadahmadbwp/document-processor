from django.core.cache import cache
import hashlib
from document_processor_app.tasks import process_document
from .cache_utils import get_document_cache, set_document_cache
from celery.exceptions import OperationalError
import time
import json

def get_hash(file):
    content = file.read()
    file.seek(0)  # Reset pointer after reading
    return hashlib.sha256(content).hexdigest()

def get_cache_key(file_hash):
    return f"doc:{file_hash}"

def set_document_cache(file_hash, status, task_id=None):
    cache_key = get_cache_key(file_hash)
    cache_data = {
        'status': status,
        'task_id': task_id
    }
    cache.set(cache_key, json.dumps(cache_data), timeout=86400)  # 24 hours

def get_document_cache(file_hash):
    cache_key = get_cache_key(file_hash)
    data = cache.get(cache_key)
    return json.loads(data) if data else None

def enqueue_document(file):
    file_hash = get_hash(file)
    
    # Check if document is already being processed
    cache_data = get_document_cache(file_hash)
    if cache_data:
        if cache_data.get('status') == "queued" and cache_data.get('task_id') is None:
            file_content = file.read()
            file_name = file.name
            task = create_task_with_retry(file_content, file_name, file_hash)
            set_document_cache(file_hash, "queued", task.id)
            return {"hash": file_hash, "task_id": task.id}
        else:
            return {"hash": file_hash, "task_id": cache_data.get('task_id')}

    # Read file content
    file_content = file.read()
    file_name = file.name

    # Create new task with retry
    task = create_task_with_retry(file_content, file_name, file_hash)
    
    # Store in cache
    set_document_cache(file_hash, "queued", task.id)
    
    return {"hash": file_hash, "task_id": task.id}

def create_task_with_retry(file_content, file_name, file_hash, max_retries=5, retry_delay=2):
    """Create a Celery task with retry mechanism"""
    for attempt in range(max_retries):
        try:
            return process_document.delay(file_content, file_name, file_hash)
        except OperationalError as e:
            if attempt == max_retries - 1:  # Last attempt
                raise e
            time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
