import logging
import traceback
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http import JsonResponse

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except (Http404, PermissionDenied):
            # Let Django handle these normally (they result in 403/404)
            raise
        except Exception as e:
            # Log the full error with traceback
            logger.error(
                f"Unhandled exception occurred: {str(e)}\n"
                f"Path: {request.path}\n"
                f"Method: {request.method}\n"
                f"Traceback: {traceback.format_exc()}"
            )
            
            # Return a generic success response with error message
            return JsonResponse({
                "success": True,
                "message": "An unexpected error occurred. Please try again later.",
                "error": str(e)
            }, status=200) 