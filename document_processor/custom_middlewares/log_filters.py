import logging
from custom_middlewares.request_context import get_current_request_id

class RequestIDFilter(logging.Filter):
    """
    Add request_id to all log records if available in thread local storage.
    """
    def filter(self, record):
        request_id = get_current_request_id()
        record.request_id = request_id if request_id else 'no-request-id'
        return True