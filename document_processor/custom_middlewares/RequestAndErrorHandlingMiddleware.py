import logging
import traceback
import uuid
from django.utils.timezone import now
from django.db import connection
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import JsonResponse
from custom_middlewares.request_context import set_current_request_id, clear_current_request_id


logger = logging.getLogger(__name__)

class RequestAndErrorHandling:
    """
    Combined middleware that handles request logging and error handling.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = now()

        # Get IPs
        client_ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0] or request.META.get('REMOTE_ADDR')
        lb_ip = request.META.get('REMOTE_ADDR')
        request_id = request.META.get('HTTP_X_REQUEST_ID', str(uuid.uuid4()))

        # Store request_id in thread-local storage for logging
        set_current_request_id(request_id)
        
        # Store request_id in request for use in views
        request.request_id = request_id

        try:
            body = request.body.decode('utf-8')
        except Exception:
            body = '<unable to decode body>'

        # Process the request
        try:
            response = self.get_response(request)
            status_code = response.status_code
        except (Http404, PermissionDenied):
            # Let Django handle these normally
            raise
        except Exception as e:
            # Handle other exceptions
            response = self.process_exception(request, e)
            status_code = response.status_code
        
        # Calculate request duration
        duration = (now() - start_time).total_seconds()

        # Log request details
        logger.info(
            f"[{start_time}] {request_id} {request.method} {request.path} | "
            f"Client IP: {client_ip} | LB IP: {lb_ip} | Status: {status_code} | Time: {duration:.3f}s | "
            f"Body: {body[:1000]}{'... (truncated)' if len(body) > 1000 else ''}"
        )

        # Add request_id to response headers
        response['X-Request-ID'] = request_id
        
        # Add timing information
        response['X-Response-Time'] = f"{duration:.3f}s"

        # Clear thread-local storage
        clear_current_request_id()

        return response
    
    def process_exception(self, request, exception):
        """
        Process exceptions that occur during request handling.
        """
        try:
            body = request.body.decode('utf-8')
        except Exception:
            body = '<unable to decode body>'

        # Log the full error with traceback
        logger.error(
            f"Unhandled exception occurred: {str(exception)}\n"
            f"Path: {request.path}\n"
            f"Method: {request.method}\n"
            f"Body: {body}\n"
            f"Request ID: {getattr(request, 'request_id', 'unknown')}\n"
            f"Traceback: {traceback.format_exc()}"
        )
        
        # Return a generic success response with error message
        return JsonResponse({
            "success": False,
            "message": "An unexpected error occurred. Please try again later.",
            "error": str(exception),
            "request_id": getattr(request, 'request_id', 'unknown')
        }, status=500)