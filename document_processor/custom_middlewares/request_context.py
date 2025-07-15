"""
Module for storing and retrieving request-specific context data.
"""
import threading

# Thread-local storage
_thread_locals = threading.local()

def get_current_request_id():
    """Get the current request ID from thread-local storage."""
    return getattr(_thread_locals, 'request_id', None)

def set_current_request_id(request_id):
    """Set the current request ID in thread-local storage."""
    _thread_locals.request_id = request_id

def clear_current_request_id():
    """Clear the current request ID from thread-local storage."""
    if hasattr(_thread_locals, 'request_id'):
        del _thread_locals.request_id
