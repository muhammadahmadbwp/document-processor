from django.core.cache import cache
import json

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